// Importamos React
import React from "react";

// Importamos ReactDOM, que permite trabajar con el DOM del navegador
import ReactDOM from "react-dom/client";

// Importamos el componente principal App
import App from "./App";

// Creamos una raíz de React en el elemento con id "root" (definido en el HTML)
const root = ReactDOM.createRoot(document.getElementById("root"));

// Renderizamos el componente App dentro de la raíz
root.render(<App />);