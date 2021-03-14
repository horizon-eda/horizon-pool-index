#!/usr/bin/env python3
import sys
sys.path.append("../horizon-pub/build")
import horizon
from pathlib import Path
import yaml
import tempfile
import pygit2
import json
import sqlite3

version = 1

all_pools = {}

with tempfile.TemporaryDirectory() as tmpdirname:
	pool_dirs = {}
	for pool_file in Path("pools").iterdir() :
		pool_yaml = yaml.load(pool_file.open("r"), Loader=yaml.SafeLoader)
		print(pool_yaml)
		if pool_yaml["source"]["type"] == "github" :
			user = pool_yaml["source"]["user"]
			repo = pool_yaml["source"]["repo"]
			level = pool_yaml["level"]
			if level not in ("core", "extra", "community") :
				raise ValueError("unsupported level " + level)
			repo_dir = Path(tmpdirname)/(user + "-" + repo)
			pygit2.clone_repository("https://github.com/%s/%s.git"%(user,repo), str(repo_dir))
			horizon.PoolManager.add_pool(str(repo_dir))
			pool_dirs[repo_dir] = pool_yaml

	for repo_dir, pool_yaml in pool_dirs.items():
		pool_json = json.load((repo_dir / "pool.json").open("r"))
		pool_uu = pool_json["uuid"]
		pool_info = {
			"uuid": pool_uu,
			"name": pool_json["name"],
			"level": pool_yaml["level"],
			"source": pool_yaml["source"]
		}
		if pool_uu in all_pools :
			raise ValueError("duplicate pool UUID " + pool_uu)

		horizon.PoolManager.add_pool(str(repo_dir))
		horizon.Pool.update(str(repo_dir))

		con = sqlite3.connect(repo_dir / "pool.db")
		cur = con.cursor()
		cur.execute("SELECT type, COUNT(*) FROM all_items_view WHERE pool_uuid = ? GROUP BY type", (pool_uu,))
		pool_info["type_stats"] = dict(cur.fetchall())
		cur.execute('SELECT uuid FROM pools_included WHERE level != 0 ORDER BY level ASC')
		pool_info["included"] = [x[0] for x in cur.fetchall()]
		con.close()

		all_pools[pool_uu] = pool_info
	for repo_dir, pool_yaml in pool_dirs.items():
		horizon.PoolManager.remove_pool(str(repo_dir))


j = {"pools": all_pools, "version": version}
with open(sys.argv[1], "w") as fi:
	json.dump(j, fi, sort_keys=True, indent=4)
