#!/bin/bash

# rm -r /virtual/dongshu4/URLShortner/
# mkdir -p /virtual/dongshu4/URLShortner
# cp urlMap.db /virtual/dongshu4/URLShortner/
FILE=/virtual/$USER/URLShortner/urlMap.db
if ! [[ -f "$FILE" ]]; then
    rm -r /virtual/$USER/URLShortner/
    mkdir -p /virtual/$USER/URLShortner
    cp urlMap.db /virtual/$USER/URLShortner/
fi

pkill python
python3 ./PythonImplementation/URLShortner.py
