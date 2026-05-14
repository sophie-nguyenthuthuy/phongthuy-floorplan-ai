import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";

import { AnalysisScreen } from "@/screens/AnalysisScreen";
import { CungMenhScreen } from "@/screens/CungMenhScreen";
import { HomeScreen } from "@/screens/HomeScreen";
import { UploadScreen } from "@/screens/UploadScreen";

export type RootStackParamList = {
  Home: undefined;
  Upload: undefined;
  CungMenh: undefined;
  Analysis: { floorPlanId: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: "Phong Thủy AI" }}
        />
        <Stack.Screen
          name="Upload"
          component={UploadScreen}
          options={{ title: "Tải bản vẽ" }}
        />
        <Stack.Screen
          name="CungMenh"
          component={CungMenhScreen}
          options={{ title: "Cung mệnh" }}
        />
        <Stack.Screen
          name="Analysis"
          component={AnalysisScreen}
          options={{ title: "Phân tích" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
