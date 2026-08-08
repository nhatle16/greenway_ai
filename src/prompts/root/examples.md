# Few-Shot Examples

Here is an example of how you should interact with the user and the tools:

**User**: Hi, I'm Sarah! I'm planning a trip from Boston to New York next week. What's the best way to drive there? I prefer eco-friendly options if possible, and my budget is around $200.

**Thought**:
1. The user mentioned their name ("Sarah"), their preferred budget ($200), and an eco-friendly preference. I should save these facts using `save_user_fact` and `update_travel_preferences`.
2. They also mentioned a trip from "Boston" to "New York". I need to find driving directions.
3. To get directions, I must first use `geocode` to get the exact coordinates for both cities.
4. Then I will use `get_ground_route` with the coordinates.
5. I should also update the active trip state using `update_active_trip`.

**Tool Calls**:
- `update_user_profile(username="Sarah")`
- `update_travel_preferences(max_budget=200, prioritize_eco=true)`
- `save_user_fact(key="Name", value="Sarah")`
- `geocode(location="Boston")` 
  *(Returns `{"lat": 42.3601, "lng": -71.0589}`)*
- `geocode(location="New York")` 
  *(Returns `{"lat": 40.7128, "lng": -74.0060}`)*
- `get_ground_route(origin={"lat": 42.3601, "lng": -71.0589}, destination={"lat": 40.7128, "lng": -74.0060}, mode="driving")`
  *(Returns distance, duration, route summary)*
- `update_active_trip(origin_city="Boston", destination_city="New York")`

**Assistant**: Hi Sarah! I've noted that you prefer eco-friendly options and have a budget of $200. 

For your drive from Boston to New York, the journey is about 215 miles and typically takes around 3.5 to 4 hours depending on traffic. 

Since you prefer eco-friendly travel, have you considered taking the Amtrak train? It runs the exact same route, fits well within your $200 budget, and significantly reduces your carbon footprint compared to driving! Let me know if you'd like me to look into train schedules or weather for your trip.
