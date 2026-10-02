# Catalog

Everything research has ever read, chosen or not. One JSON record per candidate, in the same
shape as `parts/`, with two differences: a record here may be a draft (it has to parse and say
`schema`, `id`, `name`, `kind`; every other field may be null). Its datasheets and photos are
downloaded by `parts.py --fetch`, because links rot — into the store on the person's own machine,
`~/.local/share/spark/sources/<sha256>/`, never into this plugin (a published plugin cannot carry
vendor documents, P61). The record keeps the pointer under `documents`: URL, checksum, file name,
the date it was fetched, and the title and version once someone has read them.

`parts.py --catalog` lists it; `parts.py --need <words>` searches it after the parts library;
`parts.py --promote <id> --project .` copies a record into a project's `parts/`, where it must
pass the full contract before a design builds with it.

The PO's rule, 2026-09-29: "whenever you find something online, even if we end up not using that
part, keep it — we want a good database in time, filled with data, photos, datasheets,
alternatives."
