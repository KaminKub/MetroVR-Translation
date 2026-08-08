using MetroTranslation.Tools;
using System;
using System.IO;

namespace json_to_uasset
{
    class Program
    {
        static int Main(string[] args)
        {
            // args: <jsonFolder> <uassetOutputFolder> [engineVersion]
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: json_to_uasset <jsonFolder> <uassetOutputFolder> [engineVersion]");
                Console.WriteLine("  engineVersion: UE4_25..UE5_7 (default UE5_2)");
                return 1;
            }
            string jsonFolderPath = args[0];
            string uassetFolderPath = args[1];
            string engineVersion = args.Length > 2 ? args[2] : "UE5_2";

            Console.WriteLine($"Source JSON Folder: {jsonFolderPath}");
            Console.WriteLine($"Output UAsset Folder: {uassetFolderPath}");
            Console.WriteLine($"Engine Version: {engineVersion}");
            Console.WriteLine();

            if (!Directory.Exists(jsonFolderPath))
            {
                Console.WriteLine($"ERROR: folder not found: {jsonFolderPath}");
                return 1;
            }

            try
            {
                var converter = new JsonToUAssetConverter(
                    jsonPath: Path.Combine(jsonFolderPath, "dummy.json"),
                    uassetOutputPath: Path.Combine(uassetFolderPath, "dummy.uasset"),
                    engineVersion: engineVersion
                );
                converter.ConvertFolderToJsonAssets(jsonFolderPath, uassetFolderPath);
                return 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
                return 1;
            }
        }
    }
}
