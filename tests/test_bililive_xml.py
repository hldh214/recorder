from dataclasses import FrozenInstanceError
from xml.etree import ElementTree

import pytest

from recorder.danmaku import parse_datetime
from recorder.danmaku.bilibili.bililive_xml import (
    BililiveCaptionArtifact,
    iter_bililive_danmaku,
    prepare_bililive_xml_caption,
)


START = '2026-07-27 18:00:00'


def test_prepare_caption_streams_danmaku_and_generates_highlights(tmp_path):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text(
        '''<?xml version="1.0" encoding="UTF-8"?>
<i>
  <d p="1.250,1,25,16777215,0,0,0,0">first</d>
  <gift p="2.000">ignored gift</gift>
  <d p="3.500,1,25,16777215,0,0,0,0">second</d>
  <d p="99,1,25,16777215,0,0,0,0">late</d>
</i>
''',
        encoding='utf8',
    )
    output_path = tmp_path / 'state' / 'recording.vtt'

    artifact = prepare_bililive_xml_caption(
        xml_path, output_path, START, duration=10
    )

    assert artifact.path == output_path
    assert artifact.status == 'ready'
    assert artifact.temporary is True
    assert artifact.dropped_out_of_range == 1
    assert artifact.error_message is None
    assert artifact.highlights == 'Highlights\n00:00 Start\n00:00:00 Top1 (2🔥)'
    vtt = output_path.read_text(encoding='utf8')
    assert vtt.startswith('WEBVTT\n')
    assert 'first' in vtt
    assert 'second' in vtt
    assert 'ignored gift' not in vtt
    assert 'late' not in vtt
    assert not output_path.with_suffix('.vtt.partial').exists()


def test_iterator_ignores_malformed_and_non_d_entries(tmp_path):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text(
        '''<i>
  <gift p="1">gift</gift>
  <d p="1">   </d>
  <d>missing p</d>
  <d p=",1">malformed p</d>
  <d p="not-a-number,1">bad timestamp</d>
  <d p="-0.1,1">negative</d>
  <d p="10.1,1">too late</d>
  <d p="2,1"> 日本語 🎙 </d>
</i>''',
        encoding='utf8',
    )
    counters = {}

    messages = list(iter_bililive_danmaku(xml_path, START, 10, counters))

    assert [message['content'] for message in messages] == ['日本語 🎙']
    assert messages[0]['generation_time'] == parse_datetime(START).timestamp() + 2
    assert counters == {
        'empty_content': 1,
        'malformed_parameters': 3,
        'dropped_out_of_range': 2,
    }


def test_zero_and_duration_boundaries_are_included_and_final_message_is_flushed(
    tmp_path,
):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text(
        '<i><d p="0,1">零 🎙</d><d p="10,1">at-duration</d></i>',
        encoding='utf8',
    )
    output_path = tmp_path / 'caption.vtt'

    artifact = prepare_bililive_xml_caption(xml_path, output_path, START, 10)

    assert artifact.status == 'ready'
    assert artifact.dropped_out_of_range == 0
    vtt = output_path.read_text(encoding='utf8')
    assert '零 🎙' in vtt
    assert 'at-duration' in vtt
    assert '\n00:00:11.000 -->' not in vtt


def test_missing_xml_returns_missing_without_output_or_partial(tmp_path):
    output_path = tmp_path / 'state' / 'recording.vtt'
    partial_path = output_path.with_suffix('.vtt.partial')
    output_path.parent.mkdir()
    partial_path.write_text('stale partial', encoding='utf8')

    artifact = prepare_bililive_xml_caption(
        tmp_path / 'missing.xml', output_path, START, 10
    )

    assert artifact == BililiveCaptionArtifact(path=None, status='missing')
    assert not output_path.exists()
    assert not partial_path.exists()


def test_malformed_xml_preserves_previous_final_and_removes_partial(tmp_path):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text('<i><d p="1">first</d>', encoding='utf8')
    output_path = tmp_path / 'state' / 'recording.vtt'
    output_path.parent.mkdir()
    output_path.write_text('previous final', encoding='utf8')
    partial_path = output_path.with_suffix('.vtt.partial')
    partial_path.write_text('stale partial', encoding='utf8')

    artifact = prepare_bililive_xml_caption(xml_path, output_path, START, 10)

    assert artifact.path is None
    assert artifact.status == 'invalid'
    assert artifact.error_message
    assert output_path.read_text(encoding='utf8') == 'previous final'
    assert not partial_path.exists()


def test_artifact_is_immutable():
    artifact = BililiveCaptionArtifact(path=None)

    with pytest.raises(FrozenInstanceError):
        artifact.status = 'invalid'


def test_iterator_uses_end_events_and_clears_every_processed_element(monkeypatch):
    ignored = ElementTree.Element('gift', {'p': '1'})
    ignored.text = 'gift'
    accepted = ElementTree.Element('d', {'p': '2,1'})
    accepted.text = 'message'
    calls = []

    def fake_iterparse(path, *, events):
        calls.append((path, events))
        return iter((('end', ignored), ('end', accepted)))

    monkeypatch.setattr(ElementTree, 'iterparse', fake_iterparse)

    messages = list(iter_bililive_danmaku('recording.xml', START, 10, {}))

    assert calls == [('recording.xml', ('end',))]
    assert [message['content'] for message in messages] == ['message']
    assert ignored.attrib == {}
    assert ignored.text is None
    assert accepted.attrib == {}
    assert accepted.text is None
