# Catalog

Everything research has ever read, chosen or not. One JSON record per candidate, in the same
shape as `parts/`, with two differences: a record here may be a draft (it has to parse and say
`schema`, `id`, `name`, `kind`; every other field may be null), and its datasheets and photos are
downloaded beside it into `catalog/<id>/` by `parts.py --fetch`, because links rot.

`parts.py --catalog` lists it; `parts.py --need <words>` searches it after the parts library;
`parts.py --promote <id> --project .` copies a record into a project's `parts/`, where it must
pass the full contract before a design builds with it.

The PO's rule, 2026-09-29: "whenever you find something online, even if we end up not using that
part, keep it — we want a good database in time, filled with data, photos, datasheets,
alternatives."
