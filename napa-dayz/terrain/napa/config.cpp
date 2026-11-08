// Napa full map (Carneros to Yountville, 20.48 km): world config
// Copy to P:\Napa\config.cpp
//
// Structure follows Bohemia's official DayZ terrain sample (DayZ-Samples/Test_Terrain,
// ADPL-SA licence) and the vanilla Chernarus+ world config.

class CfgPatches
{
	class Napa
	{
		units[] = {};
		weapons[] = {};
		requiredVersion = 0.1;
		requiredAddons[] = {"DZ_Data", "DZ_Surfaces"};
	};
};

// Main-menu scene. The cutscene directory does not have to exist;
// what matters is "\intro.<worldname>".
class CfgCharacterScenes
{
	class Napa
	{
		class loc1
		{
			// Carneros hillside, looking north-east up the valley
			target[] = {8820.0, 5660.0, 32.0};
			position[] = {8774.0, 5607.0, 1.1};
			fov = 0.5236;
			date[] = {2024, 9, 15, 10, 0};
			overcast = 0.1;
			rain = 0.0;
			fog = 0.0;
		};
	};
};

class CfgMissions
{
	class Cutscenes
	{
		class NapaMenu
		{
			directory = "\intro.Napa";
		};
	};
};

class CfgWorlds
{
	class CAWorld;
	class Napa: CAWorld
	{
		description = "Napa";

		// Position on Earth for sun, moon and stars.
		// DayZ convention: longitude positive = east, latitude positive = SOUTH.
		// Napa is 38.30 N, 122.30 W.
		longitude = -122.30;
		latitude = -38.30;

		// Exported from Terrain Builder (File > Export > WRP)
		worldName = "Napa\world\Napa.wrp";

		cutscenes[] = {"NapaMenu"};

		// Default central economy files (a mission's own files are used first)
		ceFiles = "Napa\ce";

		// No navmesh yet: infected and animals can't path on this map.
		// Generated in a later phase.

		startTime = "10:00";
		startDate = "15/9/2024";	// day/month/year: harvest season

		// Middle of the 20480 m map
		centerPosition[] = {10240.0, 10240.0, 300.0};

		clutterGrid = 1.0;
		clutterDist = 125.0;
		noDetailDist = 65.0;
		fullDetailDist = 10.0;
		volFogOffset = 0;

		class UsedTerrainMaterials
		{
			material0 = "Napa\data\napa_grass.rvmat";
			material1 = "DZ\surfaces\data\terrain\cp_grass.rvmat";
		};

		// Borrowed from Chernarus for now.
		// terrainNormalTexture is Chernarus-shaped: only affects grass shading. Replace later.
		midDetailTexture = "DZ\worlds\chernarusplus\data\middle_sat_mco.paa";
		terrainNormalTexture = "DZ\worlds\chernarusplus\data\global_nohq.paa";

		class OutsideTerrain
		{
			satellite = "DZ\worlds\chernarusplus\data\outside_sat_co.paa";
			enableTerrainSynth = false;
			class Layers
			{
				class Layer0
				{
					nopx = "DZ\surfaces\data\terrain\cp_grass_nopx.paa";
					texture = "DZ\surfaces\data\terrain\cp_grass_ca.paa";
				};
			};
		};

		// 2D map labels (in-game X, Z)
		// 2D map labels (in-game X, Z); positions from docs/map-spec.md
		class Names
		{
			class City_Napa
			{
				name = "Napa";
				position[] = {13649.0, 9835.0};
				type = "Capital";
			};
			class Local_Oxbow
			{
				name = "Oxbow";
				position[] = {13949.0, 10232.0};
				type = "Local";
			};
			class Village_Yountville
			{
				name = "Yountville";
				position[] = {7834.0, 20061.0};
				type = "Village";
			};
			class Local_VeteransHome
			{
				name = "Veterans Home";
				position[] = {6970.0, 19256.0};
				type = "Local";
			};
			class Local_Carneros
			{
				name = "Carneros";
				position[] = {8774.0, 5607.0};
				type = "Local";
			};
			class Local_StateHospital
			{
				name = "Napa State Hospital";
				position[] = {15289.0, 7925.0};
				type = "Local";
			};
			class Local_Skyline
			{
				name = "Skyline Park";
				position[] = {16690.0, 7640.0};
				type = "Local";
			};
			class Local_Airport
			{
				name = "Napa County Airport";
				position[] = {14195.0, 1534.0};
				type = "Local";
			};
		};

		// Airfield markers for the 2D map: not set yet (Napa County Airport comes with Phase 5)
		ilsPosition[] = {0, 0};
		ilsDirection[] = {1, 0.08, 0};
		ilsTaxiIn[] = {};
		ilsTaxiOff[] = {};
		drawTaxiway = false;
		class SecondaryAirports {};

		class Grid
		{
			offsetX = 0.0;
			offsetY = 0.0;
			class Zoom1
			{
				zoomMax = 0.15;
				format = "XY";
				formatX = "000";
				formatY = "000";
				stepX = 100.0;
				stepY = 100.0;
			};
			class Zoom2
			{
				zoomMax = 0.85;
				format = "XY";
				formatX = "00";
				formatY = "00";
				stepX = 1000.0;
				stepY = 1000.0;
			};
			class Zoom3
			{
				zoomMax = 1e+030;
				format = "XY";
				formatX = "0";
				formatY = "0";
				stepX = 10000.0;
				stepY = 10000.0;
			};
		};

		// Paper map item: vanilla Chernarus art for now
		mapDisplayNameKey = "#STR_CfgVehicles_ChernarusMap0";
		mapDescriptionKey = "#STR_CfgVehicles_ChernarusMap1";
		mapTextureClosed = "dz\gear\navigation\data\map_chernarus_co.paa";
		mapTextureOpened = "dz\structures\signs\tourist\data\karta_co.paa";
		mapTextureLegend = "dz\structures\signs\tourist\data\karta_side_co.paa";
		userMapPath = "dz\gear\navigation\data\usermap";

		minTreesInForestSquare = 10;
		minRocksInRockSquare = 5;

		soundMapAttenCoef = 0.01;
		class SoundMapValues
		{
			treehard = 0.03;
			treesoft = 0.03;
			bushhard = 0.0;
			bushsoft = 0.0;
			forest = 1.0;
			house = 0.3;
			church = 0.5;
		};
		class Sounds
		{
			sounds[] = {};
		};

		class Ambient {};
	};
};
