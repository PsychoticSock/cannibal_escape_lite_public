import zlib
from pathlib import Path

from AoE2ScenarioParser.scenarios.aoe2_scenario import _decompress_bytes

#p = Path('C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\savegame\\rec.aoe2record')
#p = Path('C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\resources\\_common\\scenario\\default0.aoe2scenario')

with p.open('rb') as file:
    content = file.read()

    numbers = content[:8]
    content = content[8:]

    print(numbers)

    b64_end = content.index(b'==') + 2  # Include double equals
    b64 = content[:b64_end]
    content = content[b64_end:]

    length = len(content)

    # Success at s=10
    for s in range(length):
        try:
            decompressed = _decompress_bytes(content[s:])
        except zlib.error as e:
            continue  # retry

        # Strip 0x00 char at the end
        data = decompressed[:-1].decode('utf-8')
        print(data)
        exit()