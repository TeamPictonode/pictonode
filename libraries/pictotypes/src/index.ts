// No Implied Warranty

export * from "./result";
export * from "./option";

/**
 * An empty object.
 *
 * The "export" keyword indicates that a user of this module should be able to
 * use this function. In this case, a user should be able to use this type alias.
 * A "Record" is a mapping/dictionary between two types. In other languages, this
 * is akin to a "Map".
 *
 * Record<string, never> is a map between strings and the never type. However,
 * the "never" type cannot actually exist. Therefore, this type is always an
 * empty map, which we use as a general placeholder for a lack of value.
 *
 */
export type Unit = Record<string, never>;
