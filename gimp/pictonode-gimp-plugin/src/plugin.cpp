// No Implied Warranty

#include <libgimp/gimp.h>

static void query(void) {}

static void run(const gchar *name, gint nparams, const GimpParam *param,
                gint *nreturn_vals, GimpParam **return_vals) {}

static void quit(void) {}

static void init(void) {}

GimpPlugInInfo PLUG_IN_INFO = {init, quit, query, run};

MAIN()
