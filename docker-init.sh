if [[ ! -f  configs/config.json ]]; then
    cp configs_init/* configs
fi

if [[ -n "$CONFIG_YOUTUBEDL_CMDARGS" ]]; then
    echo "$CONFIG_YOUTUBEDL_CMDARGS" > configs/youtube-dl.config
fi

python server.py