// Modules used
import axios from "axios";
import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Platform,
  ScrollView,
  StatusBar,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { SafeAreaView } from "react-native-safe-area-context";

/** Backend API base URL */
const BACKEND_URL = "https://watclassroom-api.vercel.app";

/** Font family for heading text based on platform */
const headingFont = Platform.select({
  ios: "HelveticaNeue-CondensedBold",
  android: "sans-serif-condensed",
  web: "'Roboto Condensed', Impact, sans-serif",
  default: "Impact, sans-serif",
});

/** Type for a single building dropdown item */
type BuildingItem = {
  label: string;
  value: string;
};

/** Type alias for the list of available open time slots in rooms */
type RoomTimes = string[][];

/**
 * Result data type mapping building codes to room availability:
 * {
 *   buildingCode: {
 *     roomCode: [
 *       [startTime, endTime],
 *       ...
 *     ],
 *     ...
 *   },
 *   ...
 * }
 */
type ResultData = {
  [buildingCode: string]: {
    [roomCode: string]: RoomTimes;
  };
};

/** Props for the BuildingDropdown component */
type BuildingDropdownProps = {
  open: boolean;
  value: string | null;
  items: BuildingItem[];
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setValue: React.Dispatch<React.SetStateAction<string | null>>;
  setItems: React.Dispatch<React.SetStateAction<BuildingItem[]>>;
  onSubmit: () => void;
};

/**
 * BuildingDropdown component renders a searchable dropdown for buildings
 * and a Submit button.
 * Props control dropdown state and submit callback.
 */
function BuildingDropdown({
  open,
  value,
  items,
  setOpen,
  setValue,
  setItems,
  onSubmit,
}: BuildingDropdownProps) {
  return (
    <View
      className="flex-row items-center space-x-4 font-body"
      style={{ zIndex: open ? 1000 : 0 }}
    >
      <View className="flex-1">
        <DropDownPicker
          open={open}
          value={value}
          style={{
            backgroundColor: "#000000",
            borderColor: "#ffffff",
          }}
          items={items}
          setOpen={setOpen}
          setValue={setValue}
          setItems={setItems}
          dropDownContainerStyle={{
            padding: 10,
            backgroundColor: "#000000",
            borderRadius: 8,
            ...(Platform.OS === "web"
              ? { boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)" }
              : {}),
          }}
          textStyle={{
            fontFamily: "Georgia, serif",
            fontSize: 16,
            color: "#ffffff",
          }}
          searchable={true}
          searchPlaceholder="Enter Building Name..."
          searchTextInputStyle={{
            color: "#ffffff",
            fontFamily: "Georgia, serif",
            fontSize: 16,
            backgroundColor: "#333333",
          }}
          arrowIconStyle={{ tintColor: "#ffffff" } as any}
        />
      </View>

      <TouchableOpacity
        onPress={onSubmit}
        disabled={!value}
        className={`p-4 rounded-md ${value ? "bg-heading" : "bg-element"}`}
      >
        <Text className="text-white text-center text-base font-heading">
          Submit
        </Text>
      </TouchableOpacity>
    </View>
  );
}

/** Props for ErrorMessage component */
type ErrorMessageProps = {
  message: string | null;
};

/**
 * Displays an error message in red text centered on screen.
 * Renders nothing if message is null or empty.
 */
function ErrorMessage({ message }: ErrorMessageProps) {
  if (!message) return null;

  return (
    <Text className="text-center text-red-500 font-body my-3">{message}</Text>
  );
}

/**
 * LoadingIndicator component displays a centered green spinner
 * to indicate loading state.
 */
function LoadingIndicator() {
  return (
    <ActivityIndicator
      size="large"
      color="#00ff00"
      style={{ marginVertical: 16 }}
    />
  );
}

/** Props for RoomTimesList component */
type RoomTimesListProps = {
  rooms: {
    [roomCode: string]: RoomTimes;
  };
};

/**
 * RoomTimesList lists each room and its open time intervals.
 * Each room shows the room code and its available times.
 */
function RoomTimesList({ rooms }: RoomTimesListProps) {
  return (
    <>
      {Object.entries(rooms).map(([roomCode, times]) => (
        <View key={roomCode} className="mb-2">
          <Text className="text-lg font-semibold text-default">{roomCode}</Text>
          {times.map(([start, end], i) => (
            <Text key={i} className="text-default ml-4">
              {start} - {end}
            </Text>
          ))}
        </View>
      ))}
    </>
  );
}

/** Props for BuildingList component */
type BuildingListProps = {
  resultData: ResultData;
  expandedBuildings: Record<string, boolean>;
  toggleBuilding: (buildingCode: string) => void;
};

/**
 * BuildingList maps over each building and renders a collapsible
 * section showing its rooms and available times.
 * Expansion is controlled via expandedBuildings state.
 */
function BuildingList({
  resultData,
  expandedBuildings,
  toggleBuilding,
}: BuildingListProps) {
  return (
    <>
      {Object.entries(resultData).map(([buildingCode, rooms]) => (
        <View
          key={buildingCode}
          className="mb-5 bg-heading rounded-xl border-4 border-element"
        >
          <TouchableOpacity
            onPress={() => toggleBuilding(buildingCode)}
            className={`p-4 flex-row justify-between items-center rounded-t-lg rounded-b-lg ${
              expandedBuildings[buildingCode] ? "bg-heading" : "bg-back"
            }`}
          >
            <Text
              className={`text-2xl font-heading font-bold ${
                expandedBuildings[buildingCode] ? "text-back" : "text-default"
              }`}
            >
              {buildingCode}
            </Text>
            <Text className="text-xl text-default">
              {expandedBuildings[buildingCode] ? "▲" : "▼"}
            </Text>
          </TouchableOpacity>

          {expandedBuildings[buildingCode] && (
            <View className="pl-6 pb-4">
              <RoomTimesList rooms={rooms} />
            </View>
          )}
        </View>
      ))}
    </>
  );
}

// ===

/**
 * Main screen component that:
 * - Fetches and displays building codes in a searchable dropdown
 * - Lets users select a building and fetch open classroom data
 * - Displays available rooms and their open time slots per building
 */
function Index() {
  // State for dropdown open/close
  const [open, setOpen] = useState<boolean>(false);
  // State for currently selected building code
  const [value, setValue] = useState<string | null>(null);
  // Dropdown items built from backend building list
  const [items, setItems] = useState<BuildingItem[]>([]);
  // Result data from API: available rooms and times
  const [resultData, setResultData] = useState<ResultData | null>(null);
  // Loading indicator while fetching API data
  const [loading, setLoading] = useState(false);
  // Tracks expanded/collapsed state for each building in UI
  const [expandedBuildings, setExpandedBuildings] = useState<
    Record<string, boolean>
  >({});
  // for user friendly error messsages
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Toggles expand/collapse of building section to show/hide rooms
   * @param buildingCode Building code to toggle
   */
  const toggleBuilding = (buildingCode: string) => {
    setExpandedBuildings((prev) => ({
      ...prev,
      [buildingCode]: !prev[buildingCode],
    }));
  };

  /**
   * useEffect hook to fetch all buildings on component mount.
   * Fetches from backend /all_buildings endpoint,
   * converts data to dropdown items, and sets state.
   */
  useEffect(() => {
    const fetchBuildings = async () => {
      try {
        const response = await axios.get<Record<string, { name: string }>>(
          `${BACKEND_URL}/all_buildings/`
        );

        const buildingsObject = response.data;
        const buildingsArray: BuildingItem[] = Object.entries(
          buildingsObject
        ).map(([code, info]) => ({
          label: `${code} - ${info.name}`,
          value: code,
        }));

        setItems(buildingsArray);
        setErrorMessage(null); // Clear any previous error
      } catch (error) {
        console.error("Failed to fetch buildings:", error);
        setErrorMessage("Failed to load building list. Please try again.");
      }
    };

    fetchBuildings(); // Call the async function
  }, []);

  /**
   * Fetches open classrooms for the selected building when user taps Submit.
   * Updates loading state and result data accordingly.
   */
  const handlePress = async () => {
    if (!value) return;

    setOpen(false);
    setLoading(true);
    setErrorMessage(null);

    try {
      const response = await axios.get<ResultData>(
        `${BACKEND_URL}/result/${value}`
      );
      setResultData(response.data);

      // Collapse all buildings initially
      const expandedState: Record<string, boolean> = {};
      Object.keys(response.data).forEach((buildingCode) => {
        expandedState[buildingCode] = false;
      });
      setExpandedBuildings(expandedState);
    } catch (error) {
      console.error("Failed to fetch result data:", error);
      setResultData(null);
      setErrorMessage("Failed to fetch available rooms. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-back p-6">
      {/* Main wrapper with padding and max width for centered layout */}
      <View className="flex-1 bg-back p-6 max-w-3xl mx-auto w-full">
        {/* App Title */}
        <Text
          className="text-5xl text-center text-heading font-bold mb-3 mt-3"
          style={{ fontFamily: headingFont }}
        >
          WatClassroom
        </Text>

        {/* Subtitle */}
        <Text className="text-xl text-center text-default mb-10 font-body">
          Find empty classrooms near you!
        </Text>

        {/* Hide Status Bar for mobiles */}
        <StatusBar hidden />

        {/* Label above dropdown */}
        <Text className="text-xl text-default mb-3 font-body">
          Choose your current location
        </Text>

        {/* Building selection dropdown with submit button */}
        <BuildingDropdown
          open={open}
          value={value}
          items={items}
          setOpen={setOpen}
          setValue={setValue}
          setItems={setItems}
          onSubmit={handlePress}
        />

        {/* Displays error messages if any (e.g., failed fetch) */}
        
        <ErrorMessage message={errorMessage} />
        {/* Results section inside scrollable area */}
        <ScrollView className="mt-4 bg-back px-2">
          {/* Show loading spinner while data is being fetched */}
          {loading && <LoadingIndicator />}

          {/* Prompt user to select a building initially */}
          {!loading && !resultData && (
            <Text className="text-center text-default font-ui mt-4">
              Select a building and press Submit to see available rooms and
              times.
            </Text>
          )}

          {/* No results returned from the backend */}
          {!loading && resultData && Object.keys(resultData).length === 0 && (
            <Text className="text-center text-default font-ui mt-4">
              No results to display.
            </Text>
          )}

          {/* Display list of buildings with expandable room/time info */}
          {!loading && resultData && (
            <BuildingList
              resultData={resultData}
              expandedBuildings={expandedBuildings}
              toggleBuilding={toggleBuilding}
            />
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

export default Index;
