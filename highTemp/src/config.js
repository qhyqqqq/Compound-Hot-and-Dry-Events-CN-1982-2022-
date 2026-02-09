const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || "http://127.0.0.1:5001";
const ARCGIS_BASE_URL =
  process.env.VUE_APP_ARCGIS_BASE_URL ||
  "http://localhost:6080/arcgis/rest/services";

export { API_BASE_URL, ARCGIS_BASE_URL };
