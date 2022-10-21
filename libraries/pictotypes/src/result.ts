// No Implied Warranty

import { Option } from "./option";

type ResultInnards<T, E> =
  | {
      ok: true;
      value: T;
    }
  | {
      ok: false;
      error: E;
    };

/**
 * The result of a computation.
 */
export class Result<T, E> {
  private readonly innards: ResultInnards<T, E>;

  protected constructor(innards: ResultInnards<T, E>) {
    this.innards = innards;
  }

  /**
   * Creates a successful result.
   * @param value The value of the result.
   * @returns The result.
   */
  public static ok<T, E>(value: T): Result<T, E> {
    return new Result({ ok: true, value });
  }

  /**
   * Creates a failed result.
   * @param error The error of the result.
   * @returns The result.
   */
  public static err<T, E>(error: E): Result<T, E> {
    return new Result({ ok: false, error });
  }

  /**
   * Runs one function for a successful result and another for a failed result.
   * @param ok The function to run for a successful result.
   * @param err The function to run for a failed result.
   * @returns The result of the function.
   */
  public match<R>(ok: (value: T) => R, err: (error: E) => R): R {
    if (this.innards.ok) {
      return ok(this.innards.value);
    } else {
      return err(this.innards.error);
    }
  }

  /**
   * Try to get the value of the result and throw an error if it is a failed result.
   * @returns The value of the result.
   */
  public unwrap(): T {
    return this.match(
      (value) => value,
      (error) => {
        throw error;
      }
    );
  }

  /**
   * Try to get the value of the result and return a default value if it is a failed result.
   * @param defaultValue The default value to return.
   * @returns The value of the result or the default value.
   */
  public unwrapOr(defaultValue: T): T {
    return this.match(
      (value) => value,
      (_) => defaultValue
    );
  }

  /**
   * Try to get the value of the result and return the result of a function if it is a failed result.
   * @param defaultValue The function to run to get the default value.
   * @returns The value of the result or the default value.
   */
  public unwrapOrElse(defaultValue: () => T): T {
    return this.match(
      (value) => value,
      (_) => defaultValue()
    );
  }

  /**
   * Map the value of the result.
   * @param mapper The function to map the value.
   * @returns The mapped result.
   */
  public map<U>(mapper: (value: T) => U): Result<U, E> {
    return this.match(
      (value) => Result.ok(mapper(value)),
      (error) => Result.err(error)
    );
  }

  /**
   * Map the error of the result.
   * @param mapper The function to map the error.
   * @returns The mapped result.
   */
  public mapErr<F>(mapper: (error: E) => F): Result<T, F> {
    return this.match(
      (value) => Result.ok(value),
      (error) => Result.err(mapper(error))
    );
  }

  /**
   * Get the value of the result or use another result.
   * @param other The other result to use.
   * @returns The value of the result or the value of the other result.
   */
  public or(other: Result<T, E>): Result<T, E> {
    return this.match(
      (value) => Result.ok(value),
      (_) => other
    );
  }

  /**
   * Get the value of the result or use the result of a function.
   * @param other The function to run to get the other result.
   * @returns The value of the result or the value of the other result.
   */
  public orElse(other: () => Result<T, E>): Result<T, E> {
    return this.match(
      (value) => Result.ok(value),
      (_) => other()
    );
  }

  /**
   * Get the value of the result and another result and combine them.
   * @param other The other result to combine.
   * @param combiner The function to combine the values.
   * @returns The combined result.
   */
  public and<U>(other: Result<U, E>): Result<U, E> {
    return this.match(
      (_) => other,
      (error) => Result.err(error)
    );
  }

  /**
   * Get the value of the result and the result of a function and combine them.
   * @param other The function to run to get the other result.
   * @param combiner The function to combine the values.
   * @returns The combined result.
   */
  public andThen<U>(other: (value: T) => Result<U, E>): Result<U, E> {
    return this.match(
      (value) => other(value),
      (error) => Result.err(error)
    );
  }

  /**
   * Is this a successful result?
   */
  public isOk(): boolean {
    return this.innards.ok;
  }

  /**
   * Discard the error information and return an option.
   * @returns The option.
   */
  public ok(): Option<T> {
    return this.match(
      (value) => Option.some(value),
      (_) => Option.none()
    );
  }
}

/**
 * A result containing another result. Able to be flattened.
 */
export class NestedResult<T, E> extends Result<Result<T, E>, E> {
  public constructor(result: Result<Result<T, E>, E>) {
    super(resultToInnards(result));
  }

  /**
   * Flatten the result.
   * @returns The flattened result.
   */
  public flatten(): Result<T, E> {
    return this.match(
      (value) => value,
      (error) => Result.err(error)
    );
  }
}

function resultToInnards<T, E>(result: Result<T, E>): ResultInnards<T, E> {
  return result.match<ResultInnards<T, E>>(
    (value) => ({ ok: true, value }),
    (error) => ({ ok: false, error })
  );
}

/**
 * Shorthand for Result.ok
 */
export const Ok = Result.ok;

/**
 * Shorthand for Result.err
 */
export const Err = Result.err;

/**
 * Shorthand for new NestedResult
 */
export const NestedRes = <T, E>(result: Result<Result<T, E>, E>) =>
  new NestedResult(result);
