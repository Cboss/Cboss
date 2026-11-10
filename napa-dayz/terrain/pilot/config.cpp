// Napa test patch (Carneros, 2.56 km): world config
// Copy to P:\NapaPilot\config.cpp
//
// Structure follows Bohemia's official DayZ terrain sample (DayZ-Samples/Test_Terrain,
// ADPL-SA licence) and the vanilla Chernarus+ world config.

class CfgPatches
{
	class NapaPilot
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
	class NapaPilot
	{
		class loc1
		{
			target[] = {1330.0, 1280.0, 60.0};
			position[] = {1280.0, 1230.0, 1.1};
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
		class NapaPilotMenu
		{
			directory = "\intro.NapaPilot";
		};
	};
};

class CfgWorlds
{
	class CAWorld;
	class NapaPilot: CAWorld
	{
		description = "Napa - Carneros test patch";

		// Position on Earth for sun, moon and stars.
		// DayZ convention: longitude positive = east, latitude positive = SOUTH.
		// Carneros is 38.26 N, 122.35 W.
		longitude = -122.35;
		latitude = -38.26;

		// Exported from Terrain Builder (File > Export > WRP)
		worldName = "NapaPilot\world\NapaPilot.wrp";

		cutscenes[] = {"NapaPilotMenu"};

		// Default central economy files (a mission's own files are used first)
		ceFiles = "NapaPilot\ce";

		// No navmesh yet: infected and animals can't path on this map.
		// Generated in a later phase.

		startTime = "10:00";
		startDate = "15/9/2024";	// day/month/year: harvest season

		// Middle of the 2560 m patch
		centerPosition[] = {1280.0, 1280.0, 300.0};

		clutterGrid = 1.0;
		clutterDist = 125.0;
		noDetailDist = 65.0;
		fullDetailDist = 10.0;
		volFogOffset = 0;

		class UsedTerrainMaterials
		{
			material0 = "NapaPilot\data\napa_grass.rvmat";
			material1 = "DZ\surfaces\data\terrain\cp_grass.rvmat";
		};

		// Borrowed from Chernarus for the test patch.
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
		class Names
		{
			class Local_Carneros
			{
				name = "Carneros";
				position[] = {1280.0, 1280.0};
				type = "Local";
			};
		};

		// No airfield on the test patch
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
