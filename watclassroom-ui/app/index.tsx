import axios from "axios";
import React, { useEffect, useState } from "react";
import { Platform, ScrollView, StatusBar, Text, TouchableOpacity, View } from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { SafeAreaView } from "react-native-safe-area-context";

type BuildingItem = {
  label: string;
  value: string;
};

const headingFont = Platform.select({
  ios: 'Chalkboard SE',
  android: 'Comic Sans MS',
  web: 'Comic Sans MS',
  default: 'System',
});

function Index() {
  const [open, setOpen] = useState<boolean>(false);
  const [value, setValue] = useState<string | null>(null);
  const [items, setItems] = useState<BuildingItem[]>([]);

  useEffect(() => {
    axios
      .get<Record<string, { name: string }>>("http://localhost:8000/all_buildings/")
      .then((response) => {
        const buildingsObject = response.data;
        const buildingsArray: BuildingItem[] = Object.entries(buildingsObject).map(
          ([code, info]) => ({
            label: `${code} - ${info.name}`,
            value: code,
          })
        );
        setItems(buildingsArray);
      })
      .catch((error) => {
        console.error("Failed to fetch buildings:", error);
      });
  }, []);

  const handlePress = () => {
    console.log("Selected building code:", value);
    setOpen(false); // close the dropdown if not done so automatically
  };

  return (
    <SafeAreaView className="flex-1 bg-back p-6">
    <View className="flex-1 bg-back p-6 max-w-3xl mx-auto w-full">
      <Text className="text-5xl text-center text-heading font-bold mb-3 mt-3" style={{ fontFamily: headingFont }}>
        WatClassroom
      </Text>
      <Text className="text-xl text-center text-default mb-10 font-rest">Find empty classrooms near you!</Text>
      <StatusBar hidden />
      <Text className="text-xl text-default mb-3 font-rest">Choose your current location</Text>

      <View className="flex-row items-center space-x-4 font-rest" style={{ zIndex: open ? 1000 : 0 }}>
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
                fontFamily: 'Arial, serif',
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
            <Text className="text-white text-center text-base" style={{ fontFamily: headingFont }}>Submit</Text>
          </TouchableOpacity>
        </View>

        <ScrollView className="mt-4 bg-back">
          {/* Other content if needed */}
        </ScrollView>

      </View>
    </SafeAreaView>
  );
}

export default Index;
