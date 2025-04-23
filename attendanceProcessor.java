import java.io.*;
import java.util.*;

public class attendanceProcessor {
    public static void main(String[] args) {
        String csvFile = "attendance.csv";
        String line;
        Map<String, Integer> attendanceCount = new HashMap<>();

        try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
            br.readLine(); // skip header

            while ((line = br.readLine()) != null) {
                String[] data = line.split(",");
                String name = data[0];

                attendanceCount.put(name, attendanceCount.getOrDefault(name, 0) + 1);
            }

            System.out.println("🔍 Attendance Summary:");
            for (Map.Entry<String, Integer> entry : attendanceCount.entrySet()) {
                System.out.println(entry.getKey() + " - " + entry.getValue() + " times");
            }

        } catch (IOException e) {
            System.out.println("❌ Error reading CSV: " + e.getMessage());
        }
    }
}
