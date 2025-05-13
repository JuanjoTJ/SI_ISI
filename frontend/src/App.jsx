// Impora axios para hacer peticiones HTTP
import axios from "axios";

// Importa React y el hook useState parra manejar el estado local del componente
import React, { useState } from "react";

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

      {/* Campo de texto para introducir el término de búsqueda */}
      <input
        type="text"
        placeholder="Buscar productos..."
        value={search}
        onChange={(e) => setSearch(e.target.value)} // Actualiza el estado 'search'
        style={{ marginRight: 10 }}
      />

      {/* Botón que al hacer clic ejecuta la función recolectar */}
      <button onClick={recolectar}>Recolectar</button>

      {/* Muestra la lista de productos recolectados */}
      <ul>
        {productos.map((p, idx) => (
          // Cada producto se muestra en un elemento de lista
          <li key={idx}>
            {p.nombre} - ${p.precio}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Exporta el componente App para que pueda ser utilizado en otros archivos
export default App;