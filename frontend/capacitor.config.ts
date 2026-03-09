import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.smartshield.ai",
  appName: "SmartShield AI",
  webDir: "build",
  server: {
    androidScheme: "https",
  },
  android: {
    backgroundColor: "#0f0c29",
  },
};

export default config;
