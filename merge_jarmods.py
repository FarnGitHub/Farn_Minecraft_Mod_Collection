import os
import json
import zipfile

# Paths
INSTANCE_DIR = os.path.dirname(os.path.abspath(__file__))
JARMODS_DIR = os.path.join(INSTANCE_DIR, "jarmods")
MMC_PACK = os.path.join(INSTANCE_DIR, "mmc-pack.json")
OUTPUT_JAR = os.path.join(INSTANCE_DIR, "merged_mods.jar")

# Load MMC pack JSON
with open(MMC_PACK, "r", encoding="utf-8") as f:
    mmc_data = json.load(f)

# Extract JARMOD uids in order
uid_order = []
uid_to_jar = {}
jarmodCachedName = {}

for component in mmc_data.get("components", []):
    uid = component.get("uid", "")
    jarmodName = component.get("cachedName", "")
    disabled = component.get("disabled", False)  # Default False means enabled

    if disabled:
        print(f"Skipping disabled jarmod: {jarmodName}")
        continue

    # Check for either prefix
    prefix = None
    if uid.startswith("org.multimc.jarmod."):
        prefix = "org.multimc.jarmod."
    elif uid.startswith("custom.jarmod."):
        prefix = "custom.jarmod."

    if prefix:
        obfuscated_name = uid[len(prefix):]  # strip prefix
        jar_path = os.path.join(JARMODS_DIR, f"{obfuscated_name}.jar")
        if os.path.isfile(jar_path):
            uid_order.append(uid)
            uid_to_jar[uid] = jar_path
            jarmodCachedName[uid] = jarmodName
        else:
            print(f"⚠️  Warning: Jar file not found for UID {uid}: {jar_path}")

# Merge jars into OUTPUT_JAR
merged_files = {}
merged_count = 0
skipped_count = 0

for uid in uid_order:
    jar_path = uid_to_jar.get(uid)
    jarmodName = jarmodCachedName.get(uid)
    if not jar_path:
        continue

    print(f"Merging Jar: {jarmodName}")
    merged_count += 1
    with zipfile.ZipFile(jar_path, "r") as jar_zip:
        for file in jar_zip.namelist():
            if file.startswith("META-INF/"):
                continue  # Skip META-INF signatures
            merged_files[file] = jar_zip.read(file)

# Write merged output
with zipfile.ZipFile(OUTPUT_JAR, "w") as out_zip:
    for file, data in merged_files.items():
        out_zip.writestr(file, data)

print(f"\n✅ Merged JAR created: {OUTPUT_JAR}")
print(f"✅ Total merged mods: {merged_count}")
print(f"⚙️  Skipped disabled mods: {len([c for c in mmc_data['components'] if c.get('disabled', False)])}")
input("Press Enter to exit...")

