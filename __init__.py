# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 rokkhonmin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Match an album's files to its tracks by their disc and track number tags."""

import re

from picard.album import (
    Album,
    NatAlbum,
)
from picard.plugin3.api import (
    BaseAction,
    PluginApi,
)


number_pattern = re.compile(r'\s*(\d+)')


def parse_number(value):
    """Return the leading number of a tag value such as "3" or "3/12", or None."""
    match = number_pattern.match(value)
    return int(match.group(1)) if match else None


def track_position(track):
    # orig_metadata is the release data from MusicBrainz, before tagger scripts
    metadata = track.orig_metadata
    return parse_number(metadata['discnumber']), parse_number(metadata['tracknumber'])


def track_id(track):
    return '{}-{}'.format(*track_position(track))


def file_position(file):
    # orig_metadata holds the file's own tags; metadata is the track's once matched
    metadata = file.orig_metadata
    tracknumber = parse_number(metadata['tracknumber'])
    if tracknumber is None:
        return None
    # Files without a disc number count as disc 1
    discnumber = parse_number(metadata['discnumber']) if metadata['discnumber'] else 1
    return discnumber, tracknumber


def album_name(album):
    return album.metadata['album'] or album.id


def assign_files(api, album, targets):
    """Match files to their target tracks in the album pane.

    This only changes which track Picard shows each file under. Nothing on
    disk changes until the album is saved.

    targets is a list of (file, track or None). A file is only matched if no
    other file has the same target. Other files keep their current track,
    unless another file took it, in which case they go back to the album's
    "Unmatched Files".
    """
    name = album_name(album)
    claims = {}
    unplaced = []
    for file, track in targets:
        if track is None:
            unplaced.append(file)
        else:
            claims.setdefault(track, []).append(file)

    taken = set()
    # File.move() attaches a loaded file to a track (or cluster) inside Picard
    with api.tagger.window.metadata_box.ignore_updates:
        for track, files in claims.items():
            if len(files) == 1:
                files[0].move(track)
                taken.add(track)
            else:
                api.logger.warning('%s: %d files belong on track %s, leaving them as they are: %s',
                                   name, len(files), track_id(track),
                                   ', '.join(file.filename for file in files))
                unplaced.extend(files)
        for file in unplaced:
            if file.parent_item in taken:
                file.move(album.unmatched_files)
    return len(taken)


def match_by_track_number(api, album):
    name = album_name(album)
    tracks = {track_position(track): track for track in album.tracks}
    targets = []
    for file in list(album.iterfiles()):
        track = tracks.get(file_position(file))
        if track is None:
            api.logger.info('%s: no track for the disc/track number of %s', name, file.filename)
        targets.append((file, track))
    placed = assign_files(api, album, targets)
    api.tagger.window.set_statusbar_message(
        '%s: matched %d of %d files by track number', name, placed, len(targets), translate=None)


def selected_albums(objs):
    # NatAlbum holds standalone recordings, which have no track positions
    return [obj for obj in objs if isinstance(obj, Album) and not isinstance(obj, NatAlbum) and obj.loaded]


class MatchByTrackNumber(BaseAction):
    TITLE = 'Match files by track number'

    def callback(self, objs):
        for album in selected_albums(objs):
            match_by_track_number(self.api, album)


def enable(api: PluginApi):
    """Called when plugin is enabled."""
    api.register_album_action(MatchByTrackNumber)
