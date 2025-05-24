// Impora axios para hacer peticiones HTTP
import axios from "axios";
import React, { useState } from "react";
import DEFAULT_IMG from "./default_image.jpg"; // Importa la imagen por defecto

// Define el componente pricipal App
function App() {
  // Crea un estado 'productos', inicializado como un array vacío
  const [productos, setProductos] = useState([]);

  // Crea un estado 'search', para el término de búsqueda
  const [search, setSearch] = useState("");

  // Función asíncrona que se ejecuta al hacer clic en el botón "Recolectar"
  const recolectar = async () => {
    try {
      // Hace una solicitud GET al api_gateway para obtener la lista de productos
      const res = await axios.get("http://localhost:8001/productos", {
        params: { search }
      });

      // Actualiza el estado 'productos' con los datos recibidos
      setProductos(res.data);

    } catch (err) {
      // Si ocurre un error, muestra una alerta con el mensaje de error
      alert("Error al contactar al API Gateway");
    }
  };

  // Renderiza el componente
  return (
    <div style={{ padding: 20 }}>
      <h1>Recolector de Productos</h1>
      <input
        type="text"
        placeholder="Buscar productos..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginRight: 10 }}
      />
      <button onClick={recolectar}>Recolectar</button>

      <ul style={{ padding: 0 }}>
        {productos.map((p, idx) => {
          // Asegura que los arrays tengan la misma longitud
          const precios = Array.isArray(p.product_price) ? p.product_price : [p.product_price];
          const proveedores = Array.isArray(p.product_provider) ? p.product_provider : [p.product_provider];
          const urls = Array.isArray(p.product_url) ? p.product_url : [p.product_url];
          const filas = Math.max(precios.length, proveedores.length, urls.length);

          return (
            <li
              key={idx}
              style={{
                marginBottom: 20,
                listStyle: "none",
                border: "1px solid #ccc",
                padding: 10,
                display: "flex",
                alignItems: "flex-start"
              }}
            >
              {/* Imagen a la izquierda */}
              <div style={{ marginRight: 20 }}>
                <img
                  src={p.product_photo || DEFAULT_IMG}
                  alt="foto producto"
                  style={{ maxWidth: 150, maxHeight: 150, objectFit: "contain", background: "#f5f5f5" }}
                  onError={e => { e.target.onerror = null; e.target.src = DEFAULT_IMG; }}
                />
              </div>
              {/* Info a la derecha */}
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: "bold", fontSize: 18, marginBottom: 10 }}>{p.product_title}</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 2fr", gap: 10, fontSize: 15, fontWeight: "bold", marginBottom: 5 }}>
                  <div>Precio</div>
                  <div>Proveedor</div>
                  <div>URL</div>
                </div>
                {/* Filas de precios, proveedores y urls */}
                {Array.from({ length: filas }).map((_, i) => (
                  <div
                    key={i}
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr 2fr",
                      gap: 10,
                      alignItems: "center",
                      fontSize: 15
                    }}
                  >
                    <div>€{precios[i] !== undefined ? precios[i] : "-"}</div>
                    <div>{proveedores[i] !== undefined ? proveedores[i] : "-"}</div>
                    <div>
                      {urls[i] ? (
                        <a href={urls[i]} target="_blank" rel="noopener noreferrer" style={{ wordBreak: "break-all" }}>
                          {urls[i]}
                        </a>
                      ) : "-"}
                    </div>
                  </div>
                ))}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

// Exporta el componente App para que pueda ser utilizado en otros archivos
export default App;