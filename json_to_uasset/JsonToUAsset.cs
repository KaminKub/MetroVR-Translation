using System;
using System.IO;
using UAssetAPI;
using UAssetAPI.UnrealTypes;

namespace MetroTranslation.Tools
{
    /// <summary>
    /// Converts UAssetAPI JSON files back to .uasset binary.
    /// </summary>
    public class JsonToUAssetConverter
    {
        private readonly string _jsonPath;
        private readonly string _uassetOutputPath;
        private readonly string _engineVersion;

        public JsonToUAssetConverter(string jsonPath, string uassetOutputPath, string engineVersion = "UE5_2")
        {
            _jsonPath = jsonPath;
            _uassetOutputPath = uassetOutputPath;
            _engineVersion = engineVersion;
        }

        /// <summary>
        /// Convert a single JSON file to .uasset
        /// </summary>
        public void SaveJsonToUAsset()
        {
            try
            {
                Console.WriteLine($"Converting: {Path.GetFileName(_jsonPath)}");
                Console.WriteLine($"  -> {_uassetOutputPath}");
                Console.WriteLine($"  Engine: {_engineVersion}");

                // 1. Load JSON into UAssetAPI object
                var asset = UAsset.DeserializeJson(File.ReadAllText(_jsonPath));

                // 2. Write .uasset (library auto-creates .uexp/.ubulk if needed)
                asset.Write(_uassetOutputPath);

                Console.WriteLine($"  OK: {Path.GetFileName(_uassetOutputPath)}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  FAIL: {ex.Message}");
                if (ex.InnerException != null)
                    Console.WriteLine($"  Detail: {ex.InnerException.Message}");
            }
        }

        /// <summary>
        /// Convert all JSON files in a folder to .uasset, preserving relative paths.
        /// </summary>
        public void ConvertFolderToJsonAssets(string jsonFolderPath, string uassetFolderPath)
        {
            try
            {
                Console.WriteLine($"JSON folder: {jsonFolderPath}");
                Console.WriteLine($"Output folder: {uassetFolderPath}");
                Console.WriteLine();

                if (!Directory.Exists(jsonFolderPath))
                {
                    Console.WriteLine($"WARN: folder not found: {jsonFolderPath}");
                    return;
                }

                if (!Directory.Exists(uassetFolderPath))
                {
                    Directory.CreateDirectory(uassetFolderPath);
                }

                var jsonFiles = Directory.EnumerateFiles(jsonFolderPath, "*.json", SearchOption.AllDirectories).ToArray();

                if (jsonFiles.Length == 0)
                {
                    Console.WriteLine("WARN: no JSON files found");
                    return;
                }

                Console.WriteLine($"Found {jsonFiles.Length} JSON files");
                Console.WriteLine();

                int successCount = 0;
                int failCount = 0;

                foreach (var jsonFile in jsonFiles)
                {
                    var relativePath = Path.GetRelativePath(jsonFolderPath, jsonFile);
                    // strip ".json" so output is <name>.uasset (not <name>.json.uasset)
                    if (relativePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                        relativePath = relativePath.Substring(0, relativePath.Length - ".json".Length);
                    var outputPath = Path.Combine(uassetFolderPath, relativePath + ".uasset");
                    Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);

                    var converter = new JsonToUAssetConverter(jsonFile, outputPath, _engineVersion);
                    converter.SaveJsonToUAsset();

                    if (File.Exists(outputPath))
                    {
                        successCount++;
                    }
                    else
                    {
                        failCount++;
                    }
                }

                Console.WriteLine("==========================================");
                Console.WriteLine($"Summary: OK {successCount}, FAIL {failCount}");
                Console.WriteLine("==========================================");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: {ex.Message}");
            }
        }
    }
}
