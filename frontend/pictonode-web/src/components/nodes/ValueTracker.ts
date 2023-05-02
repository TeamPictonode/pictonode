// GNU AGPL v3 License
// Written by John Nunley

import { forceUpdate } from "../../forceUpdate";

export enum TrackedValueType {
  SrcImage,
  // TODO: Generalize to colors, paths, etc.
}

type CommonData = {
  node_id: string;
};

export type TrackedValue = {
  type: TrackedValueType.SrcImage;
  image: number;
} & CommonData;

export default class ValueTracker {
  private values: TrackedValue[];
  private ids: Map<string, [number, number]>;

  // Singleton.
  private static instance: ValueTracker;

  private constructor() {
    this.values = [];
    this.ids = new Map();
  }

  public static get_instance(): ValueTracker {
    if (!ValueTracker.instance) {
      ValueTracker.instance = new ValueTracker();
    }

    return ValueTracker.instance;
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
    forceUpdate();
  }

  public get_value(node_id: string): Record<string, any> {
    const result: Record<string, any> = {};

    this.values.forEach((value) => {
      if (value.node_id === node_id) {
        switch (value.type) {
          case TrackedValueType.SrcImage:
            result["image"] = value.image;
        }
      }
    });

    return result;
  }

  public get_xy(node_id: string): [number, number] {
    const data = this.ids.get(node_id);
    if (data) {
      return data;
    }
    return [0, 0];
  }

  public set_xy(node_id: string, x: number, y: number): void {
    this.ids.set(node_id, [x, y]);
  }
}
