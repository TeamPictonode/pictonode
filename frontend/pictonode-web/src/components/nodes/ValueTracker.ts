// GNU AGPL v3 License
// Written by John Nunley

export enum TrackedValueType {
  SrcImage,
  // TODO: Generalize to colors, paths, etc.
}

type CommonData = {
  node_id: string;
};

export type TrackedValue = {
  type: TrackedValueType.SrcImage;
  image_id: number;
} & CommonData;

export default class ValueTracker {
  private values: TrackedValue[];

  constructor() {
    this.values = [];
  }

  public set_value(value: TrackedValue): void {
    for (let i = this.values.length - 1; i >= 0; i--) {
      if (
        this.values[i].node_id === value.node_id &&
        this.values[i].type === value.type
      ) {
        this.values.splice(i, 1);
      }
    }

    this.values.push(value);
  }

  public get_value(node_id: string): TrackedValue[] {
    const result: TrackedValue[] = [];

    this.values.forEach((value) => {
      if (value.node_id === node_id) {
        result.push(value);
      }
    });

    return result;
  }
}
