# Match Files by Track Number

A [MusicBrainz Picard](https://picard.musicbrainz.org/) 3 plugin that matches an
album's files to its tracks by the disc and track numbers in the files' tags.

Picard matches files to tracks mostly by comparing titles. If your files' titles
differ from the release, for example romanised or translated titles against a
tracklist in another script, Picard can put files on the wrong tracks or leave
them unmatched. This plugin adds an album action that matches by position
instead.

The plugin only changes which track Picard lists each file under. It doesn't
save, rename, or move any files on disk. Your files change only when you save
the album in Picard.

## Requirements

- Picard 3.0 or later.
- Files tagged with track numbers. For releases with more than one disc, the
  files also need disc numbers.

## Installing the plugin

1. In Picard, open **Options > Options… > Plugins** and click **Install**.
2. On the **URL** tab, enter this URL in **Git URL**:

   ```text
   https://github.com/rokkhonorg-mbz/picard-plugin-match-by-track-number
   ```

3. Click **Install…**. Picard warns that the plugin isn't in the official
   registry. Confirm to continue. Picard enables the plugin after it installs
   it.

To install from the command line instead, run:

```shell
picard-cli plugins install https://github.com/rokkhonorg-mbz/picard-plugin-match-by-track-number
```

## Matching files to tracks

1. Load the release in Picard and add your files to it. For example, drag a
   cluster onto the album.
2. Right-click the album and select **Plugins > Match files by track number**.

The status bar shows how many files the plugin matched, for example
`Palette: matched 10 of 10 files by track number`.

You can select several albums and run the action on all of them at once.
Running it again on the same album changes nothing.

## How the plugin matches files

- It reads the disc and track numbers from each file's own tags. Values such as
  `03` and `3/12` work.
- A file without a disc number counts as disc 1.
- Track positions come from the MusicBrainz release, so the plugin isn't
  affected by vinyl-style track numbers such as `A1` or by your tagger scripts.
  A pregap (hidden) track at position 0 matches track number `0`.
- If two or more files have the same disc and track number, the plugin leaves
  them where they are and logs a warning.
- A file with no track number, or a number that isn't on the release, stays on
  its current track. If another file takes that track, the file moves to the
  album's **Unmatched Files**.

## Troubleshooting

If a file doesn't move to the track you expect, open **Help > View Error/Debug
Log**. The plugin logs a line for each file it couldn't place and for each group
of files that share a track number.

## Developing the plugin

To edit the plugin and see your changes without committing or pushing them:

1. Clone this repository.
2. In Picard, open **Options > Options… > Plugins**, click **Install**, and open
   the **Local** tab.
3. Select your clone in **Directory**, select **Load in-place (ignore git)**,
   and click **Install…**.

After you edit the code, select the plugin in the plugin list and click
**Reload**, or restart Picard.

## License

This plugin is licensed under the GNU General Public License, version 2 or
later. See [LICENSE](LICENSE).
