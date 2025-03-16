import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Home() {
  const [restaurants, setRestaurants] = useState([]);
  const [pizzas, setPizzas] = useState([]);
  const [selectedPizza, setSelectedPizza] = useState(""); // Pizza filter
  const [searchPizza, setSearchPizza] = useState(""); // Search input for pizzas
  const [sortType, setSortType] = useState(""); // Sorting option

  useEffect(() => {
    fetch("/restaurants")
      .then((r) => r.json())
      .then(setRestaurants);
  }, []);

  useEffect(() => {
    fetch(`/pizzas?search=${searchPizza}`)
      .then((r) => r.json())
      .then(setPizzas);
  }, [searchPizza]);

  function handleDelete(id) {
    fetch(`/restaurants/${id}`, {
      method: "DELETE",
    }).then((r) => {
      if (r.ok) {
        setRestaurants((prevRestaurants) =>
          prevRestaurants.filter((restaurant) => restaurant.id !== id)
        );
      }
    });
  }


  const filteredRestaurants = restaurants.filter((restaurant) =>
    selectedPizza
      ? restaurant.restaurant_pizzas.some((rp) => rp.pizza.name === selectedPizza)
      : true
  );


  const sortedRestaurants = [...filteredRestaurants].sort((a, b) => {
    if (sortType === "name") return a.name.localeCompare(b.name);
    if (sortType === "address") return a.address.localeCompare(b.address);
    return 0;
  });

  return (
    <section className="container">
      <h1>Restaurants</h1>

      {/* Search */}
      <label>Search for Pizza:</label>
      <input
        type="text"
        placeholder="Search pizzas"
        value={searchPizza}
        onChange={(e) => setSearchPizza(e.target.value)}
      />

      {/* Filter */}
      <label>Filter by Pizza Type:</label>
      <select onChange={(e) => setSelectedPizza(e.target.value)}>
        <option value="">All Pizzas</option>
        {pizzas.map((pizza) => (
          <option key={pizza.id} value={pizza.name}>
            {pizza.name}
          </option>
        ))}
      </select>

      {/* Sort */}
      <label>Sort by:</label>
      <select onChange={(e) => setSortType(e.target.value)}>
        <option value="">No Sorting</option>
        <option value="name">Name</option>
        <option value="address">Address</option>
      </select>

      <p>{sortedRestaurants.length} results found</p>

      {/* Display Restaurants */}
      {sortedRestaurants.map((restaurant) => (
        <div key={restaurant.id} className="card">
          <h2>
            <Link to={`/restaurants/${restaurant.id}`}>{restaurant.name}</Link>
          </h2>
          <p>Address: {restaurant.address}</p>
          <button onClick={() => handleDelete(restaurant.id)}>Delete</button>
        </div>
      ))}
    </section>
  );
}

export default Home;
