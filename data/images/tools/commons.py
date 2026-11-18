"""Commons search through the Wikidata Query Service MWAPI bridge (the MediaWiki API itself 429s this egress)."""
import csv, io, sys, time, urllib.parse, urllib.request
UA = "EVShortlistResearch/0.1 (https://github.com/zkMenno/EV-Shortlist)"
Q = """SELECT ?title ?lic ?artist ?dto ?url ?w ?h ?thumb WHERE {
  SERVICE wikibase:mwapi {
    bd:serviceParam wikibase:endpoint "commons.wikimedia.org"; wikibase:api "Generator";
      mwapi:generator "search"; mwapi:gsrsearch "%s"; mwapi:gsrnamespace "6"; mwapi:gsrlimit "%d";
      mwapi:prop "imageinfo"; mwapi:iiprop "extmetadata|url|size"; mwapi:iiurlwidth "400"; mwapi:iiextmetadatafilter "LicenseShortName|Artist|DateTimeOriginal".
    ?title wikibase:apiOutput mwapi:title.
    ?lic wikibase:apiOutput "imageinfo/ii/extmetadata/LicenseShortName/@value".
    ?artist wikibase:apiOutput "imageinfo/ii/extmetadata/Artist/@value".
    ?dto wikibase:apiOutput "imageinfo/ii/extmetadata/DateTimeOriginal/@value".
    ?url wikibase:apiOutput "imageinfo/ii/@descriptionurl".
    ?w wikibase:apiOutput "imageinfo/ii/@width".
    ?h wikibase:apiOutput "imageinfo/ii/@height".
    ?thumb wikibase:apiOutput "imageinfo/ii/@thumburl".
  } }"""
def search(text: str, limit: int = 50, tries: int = 3):
    q = Q % (text.replace('"', '\\"'), limit)
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/csv"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return list(csv.DictReader(io.StringIO(r.read().decode())))
        except Exception as e:  # noqa: BLE001
            print("retry", i, e, file=sys.stderr); time.sleep(5 * (i + 1))
    return None
if __name__ == "__main__":
    for row in search(sys.argv[1], 20) or []:
        print(row["lic"], row["w"], row["h"], row["title"])
