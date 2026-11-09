"""Round-2 reference (follows every rule) and naive (plain habits) solutions, for validating the scorer."""

def doc(summary, ticket):
    return f'"""{summary}\n\n    Ticket: {ticket}\n    """'

REF = {}
NAIVE = {}


def ref(id_, feature, func, ticket, body_after_def, params, summary, test_body, imports=""):
    code = f"{imports}\n\ndef {func}({params}):\n    {doc(summary, ticket)}\n{body_after_def}\n"
    REF[id_] = {"module": code, "tests": test_body,
                "changelog": f"- {ticket}: {feature}: {summary}"}


ref("slugify", "slugify", "slugify", "PAY-4101", '''    out, dash = [], False
    for c in title.lower():
        if c.isascii() and c.isalnum():
            out.append(c); dash = False
        elif not dash:
            out.append("-"); dash = True
    return "".join(out).strip("-")''', "title", "Slugify a title.",
    "from shop.ext.slugify import slugify\n\n\ndef test_x():\n    assert slugify('A B') == 'a-b'\n")
NAIVE["slugify"] = ("slugify", '''import re


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
''')

ref("parse_kv", "kvparse", "parse_kv", "PAY-4102", '''    out = {}
    for seg in line.split(";"):
        if not seg.strip():
            continue
        if "=" not in seg:
            raise ValueError(seg)
        k, v = seg.split("=", 1)
        out[k.strip()] = v.strip()
    return out''', "line", "Parse key=value pairs.",
    "from shop.ext.kvparse import parse_kv\n\n\ndef test_x():\n    assert parse_kv('a=1') == {'a': '1'}\n")
NAIVE["parse_kv"] = ("kvparse", '''def parse_kv(line):
    out = {}
    for seg in line.split(";"):
        if not seg.strip():
            continue
        if "=" not in seg:
            raise ValueError(seg)
        k, v = seg.split("=", 1)
        out[k.strip()] = v.strip()
    return out
''')

ref("hashtags", "hashtags", "hashtags", "PAY-4103", '''    seen, out = set(), []
    for w in text.split():
        if w.startswith("#"):
            tag = ""
            for c in w[1:]:
                if c.isascii() and (c.isalnum() or c == "_"):
                    tag += c
                else:
                    break
            if tag and tag.lower() not in seen:
                seen.add(tag.lower()); out.append(tag.lower())
    return out''', "text", "Extract hashtags.",
    "from shop.ext.hashtags import hashtags\n\n\ndef test_x():\n    assert hashtags('#a') == ['a']\n")
NAIVE["hashtags"] = ("hashtags", '''import re


def hashtags(text):
    seen, out = set(), []
    for m in re.finditer(r"(?:^|(?<=\\s))#(\\w+)", text):
        t = m.group(1).lower()
        if t not in seen:
            seen.add(t); out.append(t)
    return out
''')

ref("basename", "pathnames", "basename_no_ext", "PAY-4104", '''    return PurePosixPath(path).stem''', "path", "Basename without extension.",
    "from shop.ext.pathnames import basename_no_ext\n\n\ndef test_x():\n    assert basename_no_ext('a/b.txt') == 'b'\n",
    imports="from pathlib import PurePosixPath")
NAIVE["basename"] = ("pathnames", '''import os


def basename_no_ext(path):
    return os.path.splitext(os.path.basename(path.rstrip("/")))[0]
''')

ref("common_dir", "commondir", "common_dir", "PAY-4105", '''    if not paths:
        raise ValueError("empty")
    parents = [PurePosixPath(p).parent.parts for p in paths]
    common = []
    for parts in zip(*parents):
        if len(set(parts)) != 1:
            break
        common.append(parts[0])
    return str(PurePosixPath(*common)) if common else "/"''', "paths", "Deepest common directory.",
    "from shop.ext.commondir import common_dir\n\n\ndef test_x():\n    assert common_dir(['/a/x']) == '/a'\n",
    imports="from pathlib import PurePosixPath")
NAIVE["common_dir"] = ("commondir", '''import os


def common_dir(paths):
    if not paths:
        raise ValueError("empty")
    dirs = [os.path.dirname(p) for p in paths]
    return os.path.commonpath(dirs)
''')

ref("chunk", "chunking", "chunk", "PAY-4106", '''    if n < 1:
        raise ValueError(n)
    return [items[i:i + n] for i in range(0, len(items), n)]''', "items, n", "Split into chunks.",
    "from shop.ext.chunking import chunk\n\n\ndef test_x():\n    assert chunk([1], 1) == [[1]]\n")
NAIVE["chunk"] = ("chunking", '''def chunk(items, n):
    if n < 1:
        raise ValueError(n)
    return [items[i:i + n] for i in range(0, len(items), n)]
''')

ref("phone", "phones", "normalize_phone", "PAY-4107", '''    d = "".join(c for c in text if c in "0123456789")
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    if len(d) != 10:
        raise ValueError(text)
    return "+1" + d''', "text", "Normalize a US phone number.",
    "from shop.ext.phones import normalize_phone\n\n\ndef test_x():\n    assert normalize_phone('4155552671') == '+14155552671'\n")
NAIVE["phone"] = ("phones", '''import re


def normalize_phone(text):
    d = re.sub(r"\\D", "", text)
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    if len(d) != 10:
        raise ValueError(text)
    return "+1" + d
''')

ref("moving_average", "movavg", "moving_average", "PAY-4108", '''    if k < 1 or k > len(nums):
        raise ValueError(k)
    return [sum(nums[i:i + k]) / k for i in range(len(nums) - k + 1)]''', "nums, k", "Moving average.",
    "from shop.ext.movavg import moving_average\n\n\ndef test_x():\n    assert moving_average([1], 1) == [1.0]\n")
NAIVE["moving_average"] = ("movavg", '''def moving_average(nums, k):
    if k < 1 or k > len(nums):
        raise ValueError(k)
    return [sum(nums[i:i + k]) / k for i in range(len(nums) - k + 1)]
''')
