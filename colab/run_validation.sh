#!/bin/bash
set -x
cd /content

BIN=/content/gmaps-scraper
rm -f /content/val_*.json /content/val_*.log /content/val_done

run_city() {
  name="$1"
  lat="$2"
  lon="$3"
  shift 3

  : > "/content/q_${name}.txt"
  for q in "$@"; do
    printf '%s\n' "$q" >> "/content/q_${name}.txt"
  done

  "$BIN" \
    -input "/content/q_${name}.txt" \
    -geo "${lat},${lon}" \
    -zoom 15 \
    -lang en \
    -depth 1 \
    -c 2 \
    -json \
    -results "/content/val_${name}.json" \
    -exit-on-inactivity 2m \
    > "/content/val_${name}.log" 2>&1
}

run_city yonkers 40.9312 -73.8988 \
  "restaurants in Yonkers NY" \
  "coffee shops in Yonkers NY" \
  "hair salons in Yonkers NY" \
  "auto repair in Yonkers NY" \
  "gyms in Yonkers NY"

run_city brooklyn 40.6782 -73.9442 \
  "restaurants in Brooklyn NY" \
  "coffee shops in Brooklyn NY" \
  "nail salons in Brooklyn NY" \
  "dentists in Brooklyn NY" \
  "gyms in Brooklyn NY"

run_city jerseycity 40.7178 -74.0431 \
  "restaurants in Jersey City NJ" \
  "barbershops in Jersey City NJ" \
  "laundromats in Jersey City NJ" \
  "auto repair in Jersey City NJ" \
  "real estate agencies in Jersey City NJ"

touch /content/val_done
