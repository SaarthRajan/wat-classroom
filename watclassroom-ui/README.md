# WatClassroom Frontend

This is the React Native (Expo) frontend app for WatClassroom — find empty classrooms near you on web, Android, and iOS.

---

## Get started

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Update API url:** The app fetches data from the backend API. 
By default, the API base URL is set to:

   ```ts
   const API_BASE_URL = "https://watclassroom-api.vercel.app";
   ```
   Make sure this matches your backend URL.

3. **Start the app**

   ```bash
   npx expo start --tunnel
   ```

This will open Expo Dev Tools where you can run on Android emulator, iOS simulator, or Expo Go app

---

## Project Structure
app/ – Your main app code using file-based routing.

package.json – Project metadata and dependencies.

Other standard Expo config files.

---

## Development Tips

- Use the tunnel connection mode (--tunnel) to test on real devices easily.

- If you want to test API changes locally, update API_BASE_URL accordingly.

- For web, ensure CORS is handled properly by your backend.

---

## Learn More

[React Native docs](https://reactnative.dev/docs/getting-started)

[Expo docs](https://docs.expo.dev/)

[WatClassroom backend API docs](https://watclassroom-api.vercel.app/docs)

---

## Contributing

Feel free to fork this repo, make changes, and open pull requests. We welcome contributions!

---

## License

MIT License © 2025 Saarth Rajan