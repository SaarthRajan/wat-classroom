import { useState } from "react";
import { ScrollView, StatusBar, Text, TouchableOpacity } from "react-native";
import DropDownPicker from "react-native-dropdown-picker";
import { SafeAreaView } from "react-native-safe-area-context";

function Index() {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState(null);
  const [items, setItems] = useState([
    { label: "DWE", value: "dwe" },
    { label: "PHY", value: "phy" },
  ]);
  const handlePress = () => {
    console.log("Button pressed!");
  };
  return (
    <SafeAreaView
      className="flex-1 bg-back p-6">
      <Text className="text-5xl text-center text-heading font-bold mb-4">WatClassroom</Text>
      <StatusBar hidden />
      <Text className="text-xl text-default mb-6">Choose Nearest Building</Text>
      <DropDownPicker
        open={open}
        value={value}
        items={items}
        setOpen={setOpen}
        setValue={setValue}
        setItems={setItems}
        dropDownContainerStyle={{
          padding: 10,
          backgroundColor: "#ffffff", // You can customize background here
          borderRadius: 8, // Optional: adds rounded corners
        }}
        searchable={true}
        searchPlaceholder="Enter Building Name..."
      />

      <TouchableOpacity
        onPress={handlePress}
        className="mt-6 mx-10 bg-heading p-4 rounded-md"
      >
        <Text className="text-white text-center text-xl font-bold">Submit</Text>
      </TouchableOpacity>
      <ScrollView></ScrollView> 
      {/* Or use flatlist here to show buildings - maybe have buildings that collapse and the classrooms inside this */}
    </SafeAreaView>
  );
}

export default Index;
