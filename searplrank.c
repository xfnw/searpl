#include <sqlite3ext.h>

SQLITE_EXTENSION_INIT1

#define UNWRAP(f) \
	if (SQLITE_OK != (rc = f)) \
		goto err;

static void custom_rank(const Fts5ExtensionApi *pApi, Fts5Context *pFts,
			sqlite3_context *pCtx, int nVal,
			sqlite3_value **apVal) {
	int rc, tmatches, length;
	int matches[3] = {0};
	int score = 0;
	const char *text;

	if (pApi->xColumnCount(pFts) != 3) {
		sqlite3_result_error(pCtx,
				     "this ranking algorithm depends on a "
				     "specific number of columns",
				     -1);
		return;
	}

	UNWRAP(pApi->xInstCount(pFts, &tmatches));

	/* surely there has to be a better way to get the number of
	 * matches per column?? */
	for (int i = 0; i < tmatches; i++) {
		int ip, ic, io;
		UNWRAP(pApi->xInst(pFts, i, &ip, &ic, &io));
		matches[ic] += 1;
	}

	/* getting the column's text and discarding it seems like the
	 * easiest way to get the length. xColumnSize gives tokens */
	UNWRAP(pApi->xColumnText(pFts, 0, &text, &length));
	score += 30000 * matches[0] / length; /* title */
	UNWRAP(pApi->xColumnText(pFts, 1, &text, &length));
	score += 50000 * matches[1] / length; /* url */
	UNWRAP(pApi->xColumnText(pFts, 2, &text, &length));
	score += 1000 * matches[2] / length; /* content */

	sqlite3_result_int(pCtx, score / 10);
	return;
err:
	sqlite3_result_error_code(pCtx, rc);
}

int sqlite3_searplrank_init(sqlite3 *db, char **err,
			    const sqlite3_api_routines *pApi) {
	SQLITE_EXTENSION_INIT2(pApi);

	fts5_api *fApi = 0;
	{
		sqlite3_stmt *stmt = 0;
		if (SQLITE_OK !=
		    sqlite3_prepare(db, "SELECT fts5(?1)", -1, &stmt, 0))
			return -1;
		sqlite3_bind_pointer(stmt, 1, &fApi, "fts5_api_ptr", 0);
		sqlite3_step(stmt);
		sqlite3_finalize(stmt);
	}

	return (fApi->xCreateFunction(fApi, "searplrank", 0, custom_rank, 0));
}
