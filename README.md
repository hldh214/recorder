# stream-recorder

stream recorder &amp;&amp; automatic upload

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development purposes.

### From Docker

[![Docker Stars](https://img.shields.io/docker/stars/hldh214/recorder.svg)](https://hub.docker.com/r/hldh214/recorder/)
[![Docker Pulls](https://img.shields.io/docker/pulls/hldh214/recorder.svg)](https://hub.docker.com/r/hldh214/recorder/)
[![Docker Automated buil](https://img.shields.io/docker/automated/hldh214/recorder.svg)](https://hub.docker.com/r/hldh214/recorder/)

``` sh
$ docker run -d --name recorder --restart always -v /path/to/your/config.toml:/app/config.toml -v /path/to/your/videos:/app/videos hldh214/recorder
```

### Prerequisites

```
python >= 3.5
```

### Installing

```
git clone https://github.com/hldh214/recorder.git
cd ./recorder
pip install -r requirements.txt
python recorder/recorder.py
```

## Built With

* [google-api](https://github.com/googleapis/google-api-python-client) - Brilliant api client
* [toml](https://github.com/toml-lang/toml) - Tom's Obvious, Minimal Language for configure
* [tqdm](https://github.com/tqdm/tqdm) - Progress Bar with <3

## Contribution

Feel free to contribute.

* Found a bug? Try to find it in issue tracker https://github.com/hldh214/recorder/issues ... If this bug is missing - you can add an issue about it.
* Can/want/like develop? Create pull request and I will check it in nearest time!

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/hldh214/recorder/tags). 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
