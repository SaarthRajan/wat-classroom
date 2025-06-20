import axios from "axios";
import React, { useEffect, useState } from "react";
import {
  Platform,
  ScrollView,
  StatusBar,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { SafeAreaView } from "react-native-safe-area-context";

const headingFont = Platform.select({
  ios: "Chalkboard SE",
  android: "Comic Sans MS",
  web: "Comic Sans MS",
  default: "System",
});

type BuildingItem = {
  label: string;
  value: string;
};

type RoomTimes = string[][];

type ResultData = {
  [buildingCode: string]: {
    [roomCode: string]: RoomTimes;
  };
};

function Index() {
  const [open, setOpen] = useState<boolean>(false);
  const [value, setValue] = useState<string | null>(null);
  const [items, setItems] = useState<BuildingItem[]>([]);
  const [resultData, setResultData] = useState<ResultData | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedBuildings, setExpandedBuildings] = useState<
    Record<string, boolean>
  >({});

  const toggleBuilding = (buildingCode: string) => {
    setExpandedBuildings((prev) => ({
      ...prev,
      [buildingCode]: !prev[buildingCode],
    }));
  };

  useEffect(() => {
    axios
      .get<Record<string, { name: string }>>(
        "http://localhost:8000/all_buildings/"
      )
      .then((response) => {
        const buildingsObject = response.data;
        const buildingsArray: BuildingItem[] = Object.entries(
          buildingsObject
        ).map(([code, info]) => ({
          label: `${code} - ${info.name}`,
          value: code,
        }));
        setItems(buildingsArray);
      })
      .catch((error) => {
        console.error("Failed to fetch buildings:", error);
      });
  }, []);

  const handlePress = () => {
    if (!value) return;
    setOpen(false);
    setLoading(true);
    axios
      .get<ResultData>(`http://localhost:8000/result/${value}`)
      .then((response) => {
        setLoading(false);
        // Show all buildings from the response, no filtering
        setResultData(response.data);

        const expandedState: Record<string, boolean> = {};
        Object.keys(response.data).forEach((buildingCode) => {
          expandedState[buildingCode] = false; // or true to expand all
        });
        setExpandedBuildings(expandedState);
      })
      .catch((error) => {
        setLoading(false);
        console.error("Failed to fetch result data:", error);
        setResultData(null);
      });
  };

  return (
    <SafeAreaView className="flex-1 bg-back p-6">
      <View className="flex-1 bg-back p-6 max-w-3xl mx-auto w-full">
        <Text
          className="text-5xl text-center text-heading font-bold mb-3 mt-3"
          style={{ fontFamily: headingFont }}
        >
          WatClassroom
        </Text>
        <Text className="text-xl text-center text-default mb-10 font-rest">
          Find empty classrooms near you!
        </Text>
        <StatusBar hidden />
        <Text className="text-xl text-default mb-3 font-rest">
          Choose your current location
        </Text>

        <View
          className="flex-row items-center space-x-4 font-rest"
          style={{ zIndex: open ? 1000 : 0 }}
        >
          <View className="flex-1">
            <DropDownPicker
              open={open}
              value={value}
              items={items}
              setOpen={setOpen}
              setValue={setValue}
              setItems={setItems}
              dropDownContainerStyle={{
                padding: 10,
                backgroundColor: "#ffffff",
                borderRadius: 8,
                ...(Platform.OS === "web"
                  ? { boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)" }
                  : {}),
              }}
              textStyle={{
                fontFamily: "Arial, serif",
                fontSize: 16,
              }}
              searchable={true}
              searchPlaceholder="Enter Building Name..."
            />
          </View>

          <TouchableOpacity
            onPress={handlePress}
            disabled={!value}
            className={`p-4 rounded-md ${value ? "bg-heading" : "bg-element"}`}
          >
            <Text
              className="text-white text-center text-base"
              style={{ fontFamily: headingFont }}
            >
              Submit
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView className="mt-4 bg-back px-2">
          {!resultData && (
            <Text className="text-center text-default mt-4">
              Select a building and press Submit to see available rooms and
              times.
            </Text>
          )}

          {resultData &&
            Object.entries(resultData).map(([buildingCode, rooms]) => (
              <View
                key={buildingCode}
                className="mb-5 bg-heading"
              >
                {/* Building header */}
                <TouchableOpacity
                  onPress={() => toggleBuilding(buildingCode)}
                  className={`p-4 flex-row justify-between items-center ${
                    expandedBuildings[buildingCode]
                      ? "bg-heading"
                      : "bg-element"
                  }`}
                >
                  <Text className="text-2xl font-heading font-bold text-default">
                    {buildingCode}
                  </Text>
                  <Text className="text-xl text-default">
                    {expandedBuildings[buildingCode] ? "▲" : "▼"}
                  </Text>
                </TouchableOpacity>

                {/* Rooms list shown only if building is expanded */}
                {expandedBuildings[buildingCode] && (
                  <View className="pl-6 pb-4">
                    {Object.entries(rooms).map(([roomCode, times]) => (
                      <View key={roomCode} className="mb-2">
                        <Text className="text-lg font-semibold text-element">
                          {roomCode}
                        </Text>
                        {times.map(([start, end], i) => (
                          <Text key={i} className="text-default ml-4">
                            {start} - {end}
                          </Text>
                        ))}
                      </View>
                    ))}
                  </View>
                )}
              </View>
            ))}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

export default Index;
