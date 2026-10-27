#!/usr/bin/env python3
import master
root=master.ROOT
catalog=master.catalog(root)
index={x['id']:x for x in master.read_index(root)['packages']}
expected={f'BRC-LG05-LS{n:02}' for n in range(4,11)}
items=[x for x in catalog['packages'] if x['id'] in expected]
assert {x['id'] for x in items}==expected, 'Sieben LG05-Master erforderlich'
for item in items:
    h, hashes=master.snapshot(master.files_for(root,item))
    entry=index[item['id']]
    archive=root/master.archive_path(item)
    assert entry['version']==item['version'] and entry['master']==item['master']
    assert entry['archive']==master.archive_path(item) and entry['masterSha256']==h
    assert master.archive_matches(archive,hashes) and master.digest(archive.read_bytes())==entry['archiveSha256']
    print(item['id'], 'OK')
