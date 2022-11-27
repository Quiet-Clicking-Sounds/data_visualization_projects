from pathlib import Path
import time

import matplotlib.figure
from matplotlib import pyplot as plt

from matplotlib import ticker

plt.style.use('dark_background')
PathHome = Path().resolve()
PathArtists = PathHome / 'lyrics-master/database'

CharSet = set(list(" ETAOINSHRDLCUMWFGYPBVKJXQZ".lower()))

SongsOver2Mil = [
    ("Shape of You", "Ed Sheeran"), ("Blinding Lights", "The Weeknd"), ("Dance Monkey", "Tones And I"),
    ("Sunflower", "Post Malone"), ("One Dance", "Drake"), ("Someone You Loved", "Lewis Capaldi"),
    ("rockstar", "Post Malone"), ("Closer", "The Chainsmokers"), ("Señorita", "Shawn Mendes"),
    ("Believer", "Imagine Dragons"), ("STAY", "The Kid LAROI"), ("bad guy", "Billie Eilish"),
    ("Say You Won't Let Go", "James Arthur"), ("Perfect", "Ed Sheeran"), ("Don't Start Now", "Dua Lipa"),
    ("God's Plan", "Drake"), ("Heat Waves", "Glass Animals"), ("Lucid Dreams", "Juice WRLD"),
    ("Thinking out Loud", "Ed Sheeran"), ("Watermelon Sugar", "Harry")
]

# dropping all non-english songs because I'm too lazy to find out what counts as a word in other languages
DisallowSet = {
    '№', 'あ', 'い', 'お', 'か', 'き', 'げ', 'し', 'ち', 'て', 'り', 'ん', 'イ', 'ク', 'ブ', 'ヤ', 'ラ', 'ワ', 'ー',
    '上', '中', '价', '凶', '千', '叶', '命', '器', '娄', '子', '小', '尾', '市', '师', '废', '律', '房', '拉', '持',
    '放',
    '有', '格', '没', '王', '玛', '的', '红', '莉', '莎', '莫', '虹', '解', '遥', '酒', '队', '霓', '馆', '鸡', '黜',
    '¡',
    '§', 'ß', 'à', 'À', 'á', 'â', 'ã', 'Ä', 'ä', 'å', 'Æ', 'ç', 'Ç', 'è', 'é', 'ê', 'ë', 'Í', 'í', 'î', 'ï', 'ð', 'ñ',
    'ó', 'ô', 'Ö', 'ö', 'ø', 'ù', 'ú', 'Û', 'û', 'ü', 'Ü', 'ā', 'ę', 'ĵ', 'ł', 'œ', 'ŝ', 'ũ', '̈', 'Α', 'Β', 'Γ', 'Δ',
    'Ε', 'Η', 'Θ', 'Κ', 'Λ', 'Ν', 'Ξ', 'Ο', 'Ρ', 'Τ', 'Φ', 'Ω', 'а', 'б', 'Б', 'в', 'В', 'г', 'Г', 'Д', 'д', 'е', 'ж',
    'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'П', 'р', 'с', 'С', 'т', 'у', 'х', 'ц', 'ч', 'ы', 'ь', 'ю', 'я', 'ё',
    'ṗ', 'ẗ',
}
marker_colour = [(a, b) for a in 'h*Pps84321xX' for b in 'rgb']

all_characters_set = set()


class Song:
    def __init__(self, p: Path):
        self.artist: str
        self.album: str
        self.song: str
        self.lyrics: list[str]
        self.artist, self.album, self.name = p.parts[-3:]
        with open(p, 'r', encoding='utf8') as file:
            file_data = ''.join(file.readlines())
        if len(set(file_data) & DisallowSet) > 0:
            raise Exception("non-english song, ignoring because lazy")
        lyrics = file_data.split('________' + '_' * len(self.name))[0]
        lyrics = lyrics.lower().replace('\n', ' ')
        self.lyrics = ''.join([c for c in lyrics if c in CharSet]).split(' ')

    def total_unique_words_in_lyrics(self):
        return len(set(self.lyrics))

    def total_words_in_lyrics(self):
        return len(self.lyrics)

    def string(self) -> str:
        return f'{self.artist} - {self.name} | ' \
               f'TW:{self.total_words_in_lyrics()}, ' \
               f'UW:{self.total_unique_words_in_lyrics()}'


def get_song_path_generator(p: Path):
    """
    searches all paths below the first given path

    :param p: base path to search for files
    """
    for pn in p.iterdir():
        if pn.is_file():
            yield pn
        elif pn.is_dir():
            for par in get_song_path_generator(pn):
                yield par


def plotter(songs: list[Song]):
    # groups for
    unique_words = []
    total_words = []
    minimum_interesting_unique = 400
    minimum_interesting_total = 1000
    named_items = []
    for s in songs:
        u_words = s.total_unique_words_in_lyrics()
        t_words = s.total_words_in_lyrics()
        if u_words < 0 or t_words < 0:
            # drop anything without lyrics
            continue
        elif any([
            u_words > minimum_interesting_unique,  # lots of unique words
            t_words > minimum_interesting_total,  # lots of words
            # show songs along the bottom axis, they look mildly interesting
            (t_words > 500 and u_words < 50),
            # small difference between unique and total ( ignoring the lyrically dead songs)
            (abs(u_words - t_words) < 50 and t_words > 200),
            # see if it can find some of the most well known songs
            (s.name, s.artist) in SongsOver2Mil,
        ]):
            named_items.append(
                (u_words, t_words, s.string())
            )
        else:
            # this fills the data lists for words without markers,
            unique_words.append(u_words)
            total_words.append(t_words)

    fig: matplotlib.figure.Figure
    ax: matplotlib.figure.Axes
    fig, ax = plt.subplots(1, 1)

    ax.scatter(total_words, unique_words, marker='.')
    ax.set(
        xlabel="Total Words",
        ylabel="Unique Words",
    )
    named_items.sort(key=lambda uts: uts[0] + uts[1], reverse=True)
    mc = marker_colour.__iter__()
    for (u_words, t_words, s) in named_items:
        try:
            (m, c) = mc.__next__()
        except StopIteration:
            mc = marker_colour.__iter__()
            (m, c) = mc.__next__()
        ax.plot(t_words, u_words, ' ', marker=m, color=c, label=s, markersize=10)
    # ax.set_xscale("log")
    ax.set_xlim(1)
    # ax.set_yscale("log")
    ax.set_ylim(1)

    formatter0 = ticker.FormatStrFormatter("$%g$")
    ax.xaxis.set_major_formatter(formatter0)
    ax.yaxis.set_major_formatter(formatter0)

    ax.legend()
    plt.show()


if __name__ == '__main__':
    t0 = time.time_ns()
    songs = []
    for tar in get_song_path_generator(PathArtists):
        try:
            songs.append(Song(tar))
        except Exception:
            pass
    plotter(songs)
    t1 = time.time_ns() - t0
    print(list(all_characters_set))
    print(f"Time Taken: {t1 / 1000000:,.3f}ms")
