// No Implied Warranty

import { Result, Ok, Err, NestedRes, Option, Some, None } from "../src";
import { expect } from "chai";

describe("Result", () => {
  it("should be able to create an Ok", () => {
    const result = Ok(5);
    expect(result).to.be.instanceOf(Result);
    expect(result.unwrap()).to.equal(5);
  });

  it("should be able to create an Err", () => {
    const result = Err("error");
    expect(result).to.be.instanceOf(Result);
    expect(() => result.unwrap()).to.throw();
  });

  it("should be able to match an Ok", () => {
    const result = Ok(5);
    expect(
      result.match(
        (value) => value,
        (error) => error
      )
    ).to.equal(5);
  });

  it("should be able to match an Err", () => {
    const result = Err("error");
    expect(
      result.match(
        (value) => value,
        (error) => error
      )
    ).to.equal("error");
  });

  it("should unwrapOr an Ok", () => {
    const result = Ok(5);
    expect(result.unwrapOr(10)).to.equal(5);
  });

  it("should unwrapOr an Err", () => {
    const result = Err("error");
    expect(result.unwrapOr(10)).to.equal(10);
  });

  it("should unwrapOrElse an Ok", () => {
    const result = Ok(5);
    expect(result.unwrapOrElse(() => 10)).to.equal(5);
  });

  it("should unwrapOrElse an Err", () => {
    const result = Err("error");
    expect(result.unwrapOrElse(() => 10)).to.equal(10);
  });

  it("should map an Ok", () => {
    const result = Ok(5);
    expect(result.map((value) => value + 1).unwrap()).to.equal(6);
  });

  it("should map an Err", () => {
    const result = Err("error");
    expect(() => result.map((value: number) => value + 1).unwrap()).to.throw();
  });

  it("should mapErr an Ok", () => {
    const result = Ok(5);
    expect(result.mapErr((error) => error + "error").unwrap()).to.equal(5);
  });

  it("should mapErr an Err", () => {
    const result = Err("error");
    expect(() => result.mapErr((error) => error + "error").unwrap()).to.throw();
  });

  it("should or two Oks", () => {
    const result = Ok(5);
    expect(result.or(Ok(10)).unwrap()).to.equal(5);
  });

  it("should or an Ok and an Err", () => {
    const result = Ok(5);
    expect(result.or(Err("error")).unwrap()).to.equal(5);
  });

  it("should or an Err and an Ok", () => {
    const result = Err("error");
    expect(result.or(Ok(10)).unwrap()).to.equal(10);
  });

  it("should or two Errs", () => {
    const result = Err("error");
    expect(() => result.or(Err("error")).unwrap()).to.throw("error");
  });

  it("should orElse two Oks", () => {
    const result = Ok(5);
    expect(result.orElse(() => Ok(10)).unwrap()).to.equal(5);
  });

  it("should orElse an Ok and an Err", () => {
    const result = Ok(5);
    expect(result.orElse(() => Err("error")).unwrap()).to.equal(5);
  });

  it("should orElse an Err and an Ok", () => {
    const result = Err("error");
    expect(result.orElse(() => Ok(10)).unwrap()).to.equal(10);
  });

  it("should orElse two Errs", () => {
    const result = Err("error");
    expect(() => result.orElse(() => Err("error")).unwrap()).to.throw("error");
  });

  it("should and two Oks", () => {
    const result = Ok(5);
    expect(result.and(Ok(10)).unwrap()).to.equal(10);
  });

  it("should and an Ok and an Err", () => {
    const result = Ok(5);
    expect(() => result.and(Err("error")).unwrap()).to.throw("error");
  });

  it("should and an Err and an Ok", () => {
    const result = Err("error");
    expect(() => result.and(Ok(10)).unwrap()).to.throw("error");
  });

  it("should and two Errs", () => {
    const result = Err("error");
    expect(() => result.and(Err("error")).unwrap()).to.throw("error");
  });

  it("should andThen two Oks", () => {
    const result = Ok(5);
    expect(result.andThen((value) => Ok(value + 1)).unwrap()).to.equal(6);
  });

  it("should andThen an Ok and an Err", () => {
    const result = Ok(5);
    expect(() => result.andThen((_) => Err("error")).unwrap()).to.throw(
      "error"
    );
  });

  it("should andThen an Err and an Ok", () => {
    const result = Err("error");
    expect(() =>
      result.andThen((value: number) => Ok(value + 1)).unwrap()
    ).to.throw("error");
  });

  it("should andThen two Errs", () => {
    const result = Err("error");
    expect(() => result.andThen((_) => Err("error")).unwrap()).to.throw(
      "error"
    );
  });

  it("should be able to be converted to an Option", () => {
    const result = Ok(5);
    expect(result.ok()).to.be.instanceOf(Option);
    expect(result.ok().unwrap()).to.equal(5);
  });

  it("should be able to be flattened", () => {
    const result = Ok(Ok(5));
    expect(NestedRes(result).flatten().unwrap()).to.equal(5);
  });
});

describe("Option", () => {
  it("should be able to create a Some", () => {
    const option = Some(5);
    expect(option).to.be.instanceOf(Option);
    expect(option.unwrap()).to.equal(5);
  });

  it("should be able to create a None", () => {
    const option = None();
    expect(option).to.be.instanceOf(Option);
    expect(() => option.unwrap()).to.throw();
  });

  it("should be able to match a Some", () => {
    const option = Some(5);
    expect(
      option.match(
        (value) => value,
        () => 10
      )
    ).to.equal(5);
  });

  it("should be able to match a None", () => {
    const option = None();
    expect(
      option.match(
        (value) => value,
        () => 10
      )
    ).to.equal(10);
  });

  it("should unwrapOr a Some", () => {
    const option = Some(5);
    expect(option.unwrapOr(10)).to.equal(5);
  });

  it("should unwrapOr a None", () => {
    const option = None();
    expect(option.unwrapOr(10)).to.equal(10);
  });

  it("should unwrapOrElse a Some", () => {
    const option = Some(5);
    expect(option.unwrapOrElse(() => 10)).to.equal(5);
  });

  it("should unwrapOrElse a None", () => {
    const option = None();
    expect(option.unwrapOrElse(() => 10)).to.equal(10);
  });

  it("should map a Some", () => {
    const option = Some(5);
    expect(option.map((value) => value + 1).unwrap()).to.equal(6);
  });

  it("should map a None", () => {
    const option = None();
    expect(() => option.map((value: number) => value + 1).unwrap()).to.throw();
  });
});
