// GNU AGPL v3 License
// Written by John Nunley and Grace Meredith.

import { API_URL } from "./consts";

import axios from "axios";

const API = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export function uploadImage(file: File): Promise<number> {
  const formData = new FormData();
  formData.append("image", file);

  // Response will be JSON with number field "id"
  return API.post("/upload_image", formData, { responseType: "json" }).then(
    (response) => response.data.id
  );
}

export function processPipeline(pipeline: any): Promise<File> {
  // The body of the returning request will be an image file.
  return API.post("/process", pipeline, { responseType: "blob" }).then(
    (response) => response.data
  );
}

export function setRegister(credentials: any): Promise<boolean> {
  return API.post("/register", credentials, { responseType: "json" }).then(
    (response) => response.data
  );
}

export function savePipeline(pipeline: any): Promise<File> {
  // The body of the returning request will be a ZIP file.
  return API.post("/save", pipeline, { responseType: "blob" }).then(
    (response) => response.data
  );
}

export function checkLogin(credentials: any): Promise<boolean> {
  return API.post("/login", credentials, { responseType: "json" }).then(
    (response) => response.data
  );
}

export function loadPipeline(zip: File): Promise<any[]> {
  // Response will be JSON with pipeline field "pipeline"
  const formData = new FormData();
  formData.append("file", zip);

  return API.post("/load", formData, { responseType: "json" }).then(
    (response) => response.data
  );
}
