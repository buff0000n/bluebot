#!/bin/bash

IFS=,
CSV=$1
TIMESTAMPSTR=${2:-"2024-11-%02d 13:00:00"}
TEXTSTR=${3:-"Floof Month day %d: %s"}

COUNT=1
while read image text image2 image3 image4; do
  # ugh, 'read' with a CSV does weird stuff if there's a trailing comma
  # this works for trimming leading and trailing whitespace
  image2="$(echo "$image2" | xargs)"
  image3="$(echo "$image3" | xargs)"
  image4="$(echo "$image4" | xargs)"
  printf "[Day%02d]\n" "$COUNT"
  printf "text=$TEXTSTR\n" "$COUNT" "$text"
  printf "timestamp=$TIMESTAMPSTR\n" $COUNT
  printf "image.1=%s\n" "$image"
  printf "alt.1=%s\n" "$text"
  if [[ -n "$image2" && ! "$image2" = "" ]] ; then
    printf "image.2=%s\n" "$image2"
    printf "alt.2=%s\n" "$text"
  fi
  if [[ -n "$image3" && ! "$image3" = "" ]] ; then
    printf "image.3=%s\n" "$image3"
    printf "alt.3=%s\n" "$text"
  fi
  if [[ -n "$image4" && ! "$image4" = "" ]] ; then
    printf "image.4=%s\n" "$image4"
    printf "alt.4=%s\n" "$text"
  fi
  COUNT=$(( $COUNT + 1))
done < $CSV