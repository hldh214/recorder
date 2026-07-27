from dataclasses import FrozenInstanceError
import os
from xml.etree import ElementTree

import pytest

import recorder.danmaku.bilibili.bililive_xml as bililive_xml
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


def test_iterator_accepts_namespaced_d_elements(tmp_path):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text(
        '<i xmlns="urn:bililive"><d p="2,1">namespaced</d></i>',
        encoding='utf8',
    )

    messages = list(iter_bililive_danmaku(xml_path, START, 10, {}))

    assert [message['content'] for message in messages] == ['namespaced']


def test_iterator_classifies_non_finite_timestamps_as_malformed(tmp_path):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text(
        '''<i>
  <d p="NaN,1">not a time</d>
  <d p="inf,1">positive infinity</d>
  <d p="-inf,1">negative infinity</d>
  <d p="2,1">valid</d>
</i>''',
        encoding='utf8',
    )
    counters = {}

    messages = list(iter_bililive_danmaku(xml_path, START, 10, counters))

    assert [message['content'] for message in messages] == ['valid']
    assert counters == {'malformed_parameters': 3}


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
    assert vtt.count(' --> ') == 2
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


def test_missing_xml_preserves_previous_final(tmp_path):
    output_path = tmp_path / 'recording.vtt'
    output_path.write_text('previous final', encoding='utf8')

    artifact = prepare_bililive_xml_caption(
        tmp_path / 'missing.xml', output_path, START, 10
    )

    assert artifact.status == 'missing'
    assert output_path.read_text(encoding='utf8') == 'previous final'


@pytest.mark.parametrize('alias_kind', ['direct', 'symlink', 'hardlink'])
def test_output_aliasing_source_is_invalid_without_source_mutation(
    tmp_path, alias_kind
):
    xml_path = tmp_path / 'recording.xml'
    source = b'<i><d p="1">first</d></i>'
    xml_path.write_bytes(source)
    if alias_kind == 'direct':
        output_path = xml_path
    else:
        output_path = tmp_path / f'{alias_kind}.vtt'
        if alias_kind == 'symlink':
            output_path.symlink_to(xml_path)
        else:
            os.link(xml_path, output_path)

    artifact = prepare_bililive_xml_caption(
        xml_path, output_path, START, 10
    )

    assert artifact.path is None
    assert artifact.status == 'invalid'
    assert artifact.error_message == 'output path must not alias source XML'
    assert xml_path.read_bytes() == source
    assert not output_path.with_suffix(output_path.suffix + '.partial').exists()


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


def test_unexpected_second_pass_failure_removes_partial_and_preserves_final(
    tmp_path, monkeypatch
):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text('<i><d p="1">first</d></i>', encoding='utf8')
    output_path = tmp_path / 'state' / 'recording.vtt'
    output_path.parent.mkdir()
    output_path.write_text('previous final', encoding='utf8')
    partial_path = output_path.with_suffix('.vtt.partial')

    def fail_highlights(*args, **kwargs):
        raise RuntimeError('second pass failed')

    monkeypatch.setattr(bililive_xml, 'generate_highlights', fail_highlights)

    with pytest.raises(RuntimeError, match='second pass failed'):
        prepare_bililive_xml_caption(xml_path, output_path, START, 10)

    assert output_path.read_text(encoding='utf8') == 'previous final'
    assert not partial_path.exists()


@pytest.mark.parametrize('duration', [-1, float('nan'), float('inf'), 'bad'])
def test_invalid_duration_returns_invalid_and_preserves_final(tmp_path, duration):
    xml_path = tmp_path / 'recording.xml'
    xml_path.write_text('<i><d p="0">first</d></i>', encoding='utf8')
    output_path = tmp_path / 'recording.vtt'
    output_path.write_text('previous final', encoding='utf8')
    partial_path = output_path.with_suffix('.vtt.partial')

    artifact = prepare_bililive_xml_caption(
        xml_path, output_path, START, duration
    )

    assert artifact.path is None
    assert artifact.status == 'invalid'
    assert artifact.error_message == 'duration must be finite and non-negative'
    assert artifact.dropped_out_of_range == 0
    assert output_path.read_text(encoding='utf8') == 'previous final'
    assert not partial_path.exists()


def test_artifact_is_immutable():
    artifact = BililiveCaptionArtifact(path=None)

    with pytest.raises(FrozenInstanceError):
        artifact.status = 'invalid'


def test_iterator_uses_streaming_events_and_clears_every_processed_element(
    monkeypatch,
):
    calls = []

    def fake_iterparse(path, *, events):
        calls.append((path, events))

        def event_stream():
            root = ElementTree.Element('i')
            yield 'start', root
            ignored = ElementTree.SubElement(root, 'gift', {'p': '1'})
            ignored.text = 'gift'
            tracked_elements.append(ignored)
            yield 'start', ignored
            yield 'end', ignored
            accepted = ElementTree.SubElement(root, 'd', {'p': '2,1'})
            accepted.text = 'message'
            tracked_elements.append(accepted)
            yield 'start', accepted
            yield 'end', accepted
            yield 'end', root

        return event_stream()

    tracked_elements = []
    monkeypatch.setattr(ElementTree, 'iterparse', fake_iterparse)

    messages = list(iter_bililive_danmaku('recording.xml', START, 10, {}))

    assert calls == [('recording.xml', ('start', 'end'))]
    assert [message['content'] for message in messages] == ['message']
    assert all(element.attrib == {} for element in tracked_elements)
    assert all(element.text is None for element in tracked_elements)


def test_iterator_prunes_completed_children_from_root(monkeypatch):
    def fake_iterparse(path, *, events):
        assert path == 'large.xml'
        assert events == ('start', 'end')

        def event_stream():
            root = ElementTree.Element('i')
            yield 'start', root
            for index in range(2_000):
                assert len(root) == 0
                child = ElementTree.SubElement(root, 'd', {'p': f'{index},1'})
                child.text = f'message-{index}'
                yield 'start', child
                yield 'end', child
            yield 'end', root

        return event_stream()

    monkeypatch.setattr(ElementTree, 'iterparse', fake_iterparse)

    count = sum(
        1 for _ in iter_bililive_danmaku('large.xml', START, 2_000, {})
    )

    assert count == 2_000


def test_iterator_streams_an_integration_sized_xml_file(tmp_path):
    message_count = 10_000
    xml_path = tmp_path / 'large.xml'
    xml_path.write_text(
        '<i>'
        + ''.join(
            f'<d p="{index},1">message-{index}</d>'
            for index in range(message_count)
        )
        + '</i>',
        encoding='utf8',
    )
    counters = {}

    count = sum(
        1
        for _ in iter_bililive_danmaku(
            xml_path, START, message_count - 1, counters
        )
    )

    assert count == message_count
    assert counters == {}
