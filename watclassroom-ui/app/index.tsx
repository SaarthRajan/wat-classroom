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
  ios: "HelveticaNeue-CondensedBold",
  android: "sans-serif-condensed",
  web: "'Roboto Condensed', Impact, sans-serif",
  default: "Impact, sans-serif",
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

        setResultData(response.data);

        const expandedState: Record<string, boolean> = {};
        Object.keys(response.data).forEach((buildingCode) => {
          expandedState[buildingCode] = false; // collapse
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
        <Text className="text-xl text-center text-default mb-10 font-body">
          Find empty classrooms near you!
        </Text>
        <StatusBar hidden />
        <Text className="text-xl text-default mb-3 font-body">
          Choose your current location
        </Text>

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
                color: "#ffffff"
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
            onPress={handlePress}
            disabled={!value}
            className={`p-4 rounded-md ${value ? "bg-heading" : "bg-element"}`}
          >
            <Text
              className="text-white text-center text-base font-heading"
            >
              Submit
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView className="mt-4 bg-back px-2">
          {!resultData && (
            <Text className="text-center text-default font-ui mt-4">
              Select a building and press Submit to see available rooms and
              times.
            </Text>
          )}

          {resultData && Object.keys(resultData).length === 0 && (
            <Text className="text-center text-default font-ui mt-4">
              No results to display.
            </Text>
          )}

          {resultData &&
            Object.entries(resultData).map(([buildingCode, rooms]) => (
              <View
                key={buildingCode}
                className="mb-5 bg-heading rounded-xl border-4 border-element"
              >
                {/* Building header */}
                <TouchableOpacity
                  onPress={() => toggleBuilding(buildingCode)}
                  className={`p-4 flex-row justify-between items-center rounded-t-lg rounded-b-lg ${
                    expandedBuildings[buildingCode]
                      ? "bg-heading"
                      : "bg-back"
                  }`}
                >
                  <Text className={`text-2xl font-heading font-bold ${
                    expandedBuildings[buildingCode]
                      ? "text-back"
                      : "text-default"
                  }`}>
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
                        <Text className="text-lg font-semibold text-default">
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
