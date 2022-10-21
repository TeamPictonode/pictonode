// No Implied Warranty

import { Result } from "./result";

type OptionInnards<T> =
  | {
      defined: true;
      value: T;
    }
  | {
      defined: false;
    };

/**
 * A value that may or may not be defined.
 */
export class Option<T> {
  private readonly innards: OptionInnards<T>;

  private constructor(innards: OptionInnards<T>) {
    this.innards = innards;
  }

  /**
   * Creates an option with a value.
   * @param value The value.
   * @returns The option.
   */
  public static some<T>(value: T): Option<T> {
    return new Option({ defined: true, value });
  }

  /**
   * Creates an option without a value.
   * @returns The option.
   */
  public static none<T>(): Option<T> {
    return new Option({ defined: false });
  }

  /**
   * Runs one function for a defined option and another for an undefined option.
   * @param some The function to run for a defined option.
   * @param none The function to run for an undefined option.
   * @returns The result of the function.
   */
  public match<R>(some: (value: T) => R, none: () => R): R {
    if (this.innards.defined) {
      return some(this.innards.value);
    } else {
      return none();
    }
  }

  /**
   * Try to get the value of the option and throw an error if it is undefined.
   * @returns The value of the option.
   */
  public unwrap(): T {
    return this.match(
      (value) => value,
      () => {
        throw new Error("Option is undefined");
      }
    );
  }

  /**
   * Try to get the value of the option and return a default value if it is undefined.
   * @param defaultValue The default value.
   * @returns The value of the option or the default value.
   */
  public unwrapOr(defaultValue: T): T {
    return this.match(
      (value) => value,
      () => defaultValue
    );
  }

  /**
   * Try to get the value of the option and return the result of a function if it is undefined.
   * @param defaultValue The function to get the default value.
   * @returns The value of the option or the default value.
   */
  public unwrapOrElse(defaultValue: () => T): T {
    return this.match((value) => value, defaultValue);
  }

  /**
   * Maps the value of the option.
   * @param mapper The function to map the value.
   * @returns The mapped option.
   */
  public map<R>(mapper: (value: T) => R): Option<R> {
    return this.match(
      (value) => Option.some(mapper(value)),
      () => Option.none<R>()
    );
  }

  /**
   * Get the value of this option or use another option.
   * @param other The other option.
   * @returns The value of this option or the other option.
   */
  public or(other: Option<T>): Option<T> {
    return this.match(
      (_) => this,
      () => other
    );
  }

  /**
   * Get the value of this option or use the result of a function.
   * @param other The function to get the other option.
   * @returns The value of this option or the other option.
   */
  public orElse(other: () => Option<T>): Option<T> {
    return this.match((_) => this, other);
  }

  /**
   * Filters the value of the option.
   * @param predicate The function to filter the value.
   * @returns The filtered option.
   */
  public filter(predicate: (value: T) => boolean): Option<T> {
    return this.match(
      (value) => (predicate(value) ? this : Option.none<T>()),
      () => this
    );
  }

  /**
   * Get the value of this option and another option combined.
   * @param other The other option.
   * @returns The combined option.
   */
  public and<R>(other: Option<R>): Option<R> {
    return this.match(
      (_) => other,
      () => Option.none<R>()
    );
  }

  /**
   * Get the value of this option and the result of a function combined.
   * @param other The function to get the other option.
   * @returns The combined option.
   */
  public andThen<R>(other: (value: T) => Option<R>): Option<R> {
    return this.match(other, () => Option.none<R>());
  }

  /**
   * Is the option defined?
   */
  public isSome(): boolean {
    return this.innards.defined;
  }

  /**
   * Return a `Result` with the value of the option or an error.
   * @param error The error to return if the option is undefined.
   * @returns The `Result`.
   */
  public okOr<E>(error: E): Result<T, E> {
    return this.match(
      (value) => Result.ok(value),
      () => Result.err(error)
    );
  }

  /**
   * Return a `Result` with the value of the option or the result of a function.
   * @param error The function to get the error to return if the option is undefined.
   * @returns The `Result`.
   */
  public okOrElse<E>(error: () => E): Result<T, E> {
    return this.match(
      (value) => Result.ok(value),
      () => Result.err(error())
    );
  }
}

/**
 * Shorthand for Option.some
 */
export const Some = Option.some;

/**
 * Shorthand for Option.none
 */
export const None = Option.none;
