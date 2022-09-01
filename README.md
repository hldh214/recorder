<p align="center">
  <b>Special thanks to the generous sponsorship by:</b>
  <br><br>
  <a target="_blank" href="https://jb.gg/OpenSourceSupport">
    <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg" width=250 alt="logo">
  </a>
  <br><br>
</p>

# stream-recorder

stream recorder &amp;&amp; automatic upload

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development purposes.

### From Docker

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/hldh214/recorder/Docker%20Image%20CI.svg)](https://github.com/hldh214/recorder/pkgs/container/recorder)

``` shell
docker run -d --name recorder --restart always -v /path/to/your/config.toml:/app/config.toml -v /path/to/your/videos:/app/videos ghcr.io/hldh214/recorder
```

#### Some useful docker commands

```shell
# watch
docker exec -it recorder-recorder-1 watch -c -n 1 tree -D -C --du -h /app/videos/record

# dev kit
docker exec -it recorder-recorder-1 bash -c 'apt update && apt install -y zsh git vim tree curl && sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime && sh ~/.vim_runtime/install_awesome_vimrc.sh'

# inspect
docker exec -it recorder-recorder-1 zsh

# python interpreter
docker exec -it recorder-recorder-1 python3

# recorder module command
docker exec -it recorder-recorder-1 python3 recorder/utils/huya_danmaku_mongo.py generate-with-highlight
```

### Prerequisites

```
python >= 3.7
[node](https://github.com/nvm-sh/nvm)
[mongodb](https://www.mongodb.com/)
```

### Installing

``` shell
git clone https://github.com/hldh214/recorder.git
cd ./recorder
pip install -r requirements.txt
python -m recorder
```

## Built With

* [google-api](https://github.com/googleapis/google-api-python-client) - Brilliant api client
* [toml](https://github.com/toml-lang/toml) - Tom's Obvious, Minimal Language for configure
* [tqdm](https://github.com/tqdm/tqdm) - Progress Bar with <3
* [pyjwt](https://github.com/jpadilla/pyjwt) - JSON Web Token implementation in Python
* [cachetools](https://github.com/tkem/cachetools) - Extensible memoizing collections and decorators
* [arrow](https://github.com/arrow-py/arrow) - Better dates & times for Python
* [tenacity](https://github.com/jd/tenacity) - Retrying library for Python
* [pymongo](https://github.com/mongodb/mongo-python-driver) - The Python driver for MongoDB

## Contribution

Feel free to contribute.

* Found a bug? Try to find it in issue tracker https://github.com/hldh214/recorder/issues ... If this bug is missing -
  you can add an issue about it.
* Can/want/like develop? Create pull request and I will check it in nearest time!

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see
the [tags on this repository](https://github.com/hldh214/recorder/tags).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
