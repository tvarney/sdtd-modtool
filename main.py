
import sdtd.data
from sdtd.autolocate import get_sdtd_path

app_id = 251570

if __name__ == "__main__":
    tool = sdtd.data.ModManager()
    original = get_sdtd_path()
    modded = "./modded/"
    mods = "./sample_mods/"
    tool.run(original, modded, mods)
