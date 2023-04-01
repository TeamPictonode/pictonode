import { processPipeline } from "../../api";

//Baklava auto-recalculated the entire node tree whenever there is a change,
//so we must manually keep track of the input node's associated image & all the assigned node Ids
export let srcImgs = new Array();
export let nodeList = new Array();
export let nodeIds: { [key: string]: number } = {};
export let imgNodes: { [key: string]: number } = {};

export function getImgID(nodeId: string) {
  imgNodes[nodeId] = srcImgs[srcImgs.length - 1];
  return imgNodes[nodeId];
}

export function addNodeToPipeline(id: number, template: string, values: any) {
  return {
    id: id,
    template: template,
    metadata: {},
    values: values,
  };
}

export function addLinkToPipeline(
  id: number,
  from: number,
  to: number,
  fromIndex: number,
  toIndex: number
) {
  return {
    id: id,
    from: from,
    to: to,
    fromIndex: fromIndex,
    toIndex: toIndex,
    metadata: {},
  };
}

export function finalProcess(pipeline: any) {
  console.log("OUTPUT CALCULATE");

  processPipeline(pipeline).then((imageFile) => {
    // Create an image element and set its source to the image file.
    const image = new Image();
    image.src = URL.createObjectURL(imageFile);

    // Create a canvas element and draw the image on it.
    const canvas = <HTMLCanvasElement>document.getElementById("imgview");
    if (canvas) {
      const context = canvas.getContext("2d");

      if (!context) {
        throw new Error("Could not get canvas context");
      }

      context.clearRect(0, 0, canvas.width, canvas.height);

      image.onload = () => {
        canvas.width = image.width;
        canvas.height = image.height;
        context.drawImage(image, 0, 0);
      };
    }
  });
}
