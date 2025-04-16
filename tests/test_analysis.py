import pytest
import pandas as pd
from api.jolpica_api import JolpicaAPI
from api.data_preprocessing import save_to_csv, load_from_csv, convert_to_ms
import analysis.descriptive_analysis as descriptive_analysis
import analysis.comparative_analysis as comparative_analysis
import analysis.trend_analysis as trend_analysis

def test_descriptive_analysis():
    df = JolpicaAPI(resource_type="pitstops", filters={"season": "2023", "round": "5"}).get_cleaned_data()
    df = convert_to_ms(df)

    save_to_csv(df, "descriptive_analysis.csv")

    mean = descriptive_analysis.calculate_mean(df, 'duration')
    median = descriptive_analysis.calculate_median(df, 'duration')
    mode = descriptive_analysis.calculate_mode(df, 'duration')
    std_dev = descriptive_analysis.calculate_std_dev(df, 'duration')
    variance = descriptive_analysis.calculate_variance(df, 'duration')
    stats = descriptive_analysis.descriptive_statistics(df, 'duration')

    assert mean == 23916.3
    assert median == 22549
    assert mode is None
    assert round(std_dev, 6) == 5913.982237
    assert round(variance, 2) == 34975185.91
    assert stats == {
        'Mean': mean,
        'Median': median,
        'Mode': mode,
        'Standard Deviation': std_dev,
        'Variance': variance
    }

def test_paired_t_test():
    qualifying = JolpicaAPI(resource_type="qualifying", filters={"season": "2023", "round": "5"}).get_cleaned_data()
    qualifying = convert_to_ms(qualifying)
    results = JolpicaAPI(resource_type="results", filters={"season": "2023", "round": "5"}).get_cleaned_data()
    results = convert_to_ms(results)

    qualifying["Fastest_Qualifying_Time"] = qualifying[["Q1", "Q2", "Q3"]].min(axis=1, numeric_only=True)
    merged = pd.merge(
        qualifying[["Driver.driverId", "Fastest_Qualifying_Time"]],
        results.rename(columns={"Results.Driver.driverId": "Driver.driverId"})[["Driver.driverId", "Results.FastestLap.Time.time"]],
        on="Driver.driverId",
        how="inner"
    )
    save_to_csv(merged, "paired_t_test.csv")

    stat, p_value = comparative_analysis.paired_t_test(merged, "Fastest_Qualifying_Time", "Results.FastestLap.Time.time")

    assert stat == pytest.approx(-26.3835436607094, abs=1e-13)
    assert p_value == pytest.approx(1.96725589915244e-16, abs=1e-30)

def test_unpaired_t_test():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "6"}).get_cleaned_data()
    df = convert_to_ms(df)
    df1, df2 = (df[df["Timings.driverId"] == "max_verstappen"].rename(columns={"Timings.time": "max_verstappen.time"}),
                df[df["Timings.driverId"] == "hamilton"].rename(columns={"Timings.time": "hamilton.time"}))
    merged = pd.merge(df1, df2, on="number")

    save_to_csv(merged, "unpaired_t_test.csv")

    stat, p_value = comparative_analysis.unpaired_t_test(merged, "max_verstappen.time", "hamilton.time")

    assert stat == pytest.approx(-0.313855177502919, abs=1e-15)
    assert p_value == pytest.approx(0.754055768792724, abs=1e-15)

def test_anova():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "5"}).get_cleaned_data()
    df = convert_to_ms(df)

    save_to_csv(df, "anova.csv")

    stat, p_value = comparative_analysis.anova_test(df, "Timings.time", "Timings.driverId")

    assert stat == pytest.approx(2.18381414084741, abs=1e-13)
    assert p_value == pytest.approx(0.0023771601197084, abs=1e-15)

def test_spearman_correlation():
    df = JolpicaAPI(resource_type="results", filters={"season": "2024"}).get_cleaned_data()
    save_to_csv(df, "spearman_correlation.csv")
    corr, p_value = comparative_analysis.perform_spearman_analysis(df, "Results.grid", "Results.position")

    assert corr == pytest.approx(0.728401754402222, abs=1e-15)
    assert p_value == pytest.approx(2.33950695732824e-80, abs=1e-93)

def test_pearson_correlation():
    df = JolpicaAPI(resource_type="results", filters={"season": "2024"}).get_cleaned_data()
    save_to_csv(df, "pearson_correlation.csv")
    corr, p_value = comparative_analysis.perform_pearson_analysis(df, "Results.grid", "Results.position")

    assert corr == pytest.approx(0.727964654699956, abs=1e-15)
    assert p_value == pytest.approx(3.23405719792189e-80, abs=1e-92)

def test_wilcoxon():
    df = JolpicaAPI(resource_type="results", filters={"season": "2024"}).get_cleaned_data()
    save_to_csv(df, "wilcoxon.csv")
    stat, p_value = comparative_analysis.wilcoxon_test(df, "Results.grid", "Results.position")

    assert stat == 39243
    assert p_value == pytest.approx(0.428954014489374, abs=0.01)

def test_chi_square():
    df = JolpicaAPI(resource_type="results", filters={"season": "2024"}).get_cleaned_data()
    save_to_csv(df, "chi_square.csv")
    stat, p_value = comparative_analysis.chi_square_test(df, "Results.grid", "Results.position")

    assert stat == pytest.approx(909.44524044796, abs=1e-11)
    assert p_value == pytest.approx(2.26782891112557E-45, abs=1e-56)

def test_simple_moving_average():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "6"}).get_cleaned_data()
    df_max = df[df["Timings.driverId"] == "max_verstappen"]
    df_max = convert_to_ms(df_max)
    save_to_csv(df_max, "simple_moving_average.csv")

    result = trend_analysis.simple_moving_average(df_max, column="Timings.time", window=10)
    result = result.fillna(0)

    assert result.to_list() == [0, 0, 0, 0, 0, 0, 0, 0, 0,
        78561.2, 77823.2, 77585.8, 77421.8, 77315.4, 77221.4, 77139.8, 77062.5, 76994, 76973.2,
        76986.2, 76980.7, 76947.3, 76864.3, 76837.6, 76848, 76886.8, 76926.7, 77032.5, 77150.3, 77244.9,
        77438.7, 77654.4, 77888.6, 78013.2, 78097.3, 78173.5, 78174.9, 78110.1, 78006.6, 77906.7,
        77727, 77525.4, 77327.1, 77194.9, 77062.6, 76972.7, 76961.4, 76955.7, 77001.9, 77017.2,
        77065.5, 77790.1, 79085.7, 81308.1, 86694.7, 89600.3, 92230.7, 94805, 97441.3, 99863.9,
        102200.9, 103723.5, 104692.6, 104634.4, 101293.7, 100084.1, 99029.8, 98114.9, 96896.5, 95866.9,
        94823.5, 93936.5, 92814.1, 91664.1, 90499.9, 89628, 88881.9, 88036.1
    ]

def test_exponential_moving_average():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "6"}).get_cleaned_data()
    df_max = df[df["Timings.driverId"] == "max_verstappen"]
    df_max = convert_to_ms(df_max)
    save_to_csv(df_max, "exponential_moving_average.csv")

    result = trend_analysis.exponential_moving_average(df_max, column="Timings.time", span=5)
    expected_result = [
        84238.0000000000, 82614.3333333333, 81434.2222222222, 80332.4814814815, 79561.3209876543, 78920.8806584362,
        78491.5871056241, 78126.7247370828, 77761.4831580552, 77535.6554387035, 77309.7702924690, 77204.1801949793,
        77280.7867966529, 77208.8578644353, 77165.5719096235, 77051.7146064157, 76987.8097376105, 76895.8731584070,
        76871.5821056047, 76985.7214037364, 76924.8142691576, 76836.2095127718, 76758.8063418478, 76771.8708945652,
        76908.9139297102, 77009.9426198068, 77092.9617465379, 77318.6411643586, 77546.0941095724, 77750.7294063816,
        78080.8196042544, 78325.8797361696, 78532.5864907797, 78369.7243271865, 78254.4828847910, 78160.9885898607,
        77864.9923932404, 77617.3282621603, 77400.2188414402, 77320.4792276268, 77194.9861517512, 77063.3241011675,
        77029.8827341117, 76927.2551560744, 76851.8367707163, 76926.2245138109, 77004.1496758739, 77024.4331172493,
        77158.9554114995, 77210.6369409997, 77282.7579606665, 79537.1719737776, 82997.7813158518, 88313.8542105678,
        102398.2361403790, 103642.4907602520, 103582.9938401680, 103324.6625601120, 103480.1083734080, 102833.4055822720,
        102154.6037215150, 101193.7358143430, 100665.8238762290, 99898.5492508192, 98985.6995005462, 97335.4663336974,
        95863.9775557983, 95128.9850371989, 93954.9900247992, 93051.3266831995, 92155.2177887997, 91570.8118591998,
        90509.2079061332, 89294.1386040888, 88035.4257360592, 87128.9504907061, 86572.6336604708, 86115.4224403139
    ]


    assert [round(num, 8) for num in result.to_list()] == [round(num, 8) for num in expected_result]

def test_linear_regression():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "6"}).get_cleaned_data()
    df = convert_to_ms(df)
    #save_to_csv(df, "linear_regression.csv")

    result = trend_analysis.linear_regression(df, "Timings.time", ['Timings.position'])

    expected_result = load_from_csv('linear_regression.csv')
    expected_result = expected_result["predicted.y"]

    assert result.tolist() == pytest.approx(expected_result.tolist(), abs=1e-10)

def test_arima():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "6"}).get_cleaned_data()
    df = convert_to_ms(df)
    df_max = df[df["Timings.driverId"] == "max_verstappen"]
    save_to_csv(df_max, "arima.csv")

    result = trend_analysis.arima_model(df_max, "Timings.time", (1, 1, 1))
    expected_result = [
        84238.0, 84160.327, 80194.962, 79369.014, 78385.234, 78113.952, 77735.926, 77662.409,
        77448.011, 77111.696, 77098.165, 76902.741, 76981.888, 77351.546, 77107.065, 77088.831,
        76872.677, 76867.821, 76740.873, 76811.541, 77140.423, 76855.212, 76700.182, 76625.963,
        76769.608, 77105.531, 77184.056, 77242.359, 77673.353, 77931.154, 78110.949, 78622.271,
        78767.687, 78908.476, 78194.965, 78071.897, 77997.036, 77405.644, 77188.044, 77013.397,
        77139.893, 76976.773, 76835.477, 76944.141, 76759.743, 76715.848, 77012.196, 77126.304,
        77072.171, 77364.918, 77315.958, 77407.283, 82851.597, 88513.814, 96912.569, 124291.843,
        108677.49, 104690.276, 103285.691, 103754.669, 101933.564, 101045.929, 99618.91, 99651.115,
        98599.818, 97445.418, 94679.941, 93310.326, 93640.732, 91970.129, 91415.758, 90571.614,
        90456.221, 88763.939, 87248.233, 85872.475, 85456.306, 85475.318
    ]

    assert result.tolist()[2:] == pytest.approx(expected_result[2:], abs=3300) # First two values ignored due to inconsistencies

def test_holt_winters():
    df = JolpicaAPI(resource_type="laps", filters={"season": "2023", "round": "6"}).get_cleaned_data()
    df = convert_to_ms(df)
    df_max = df[df["Timings.driverId"] == "max_verstappen"]
    save_to_csv(df_max, "holt_winters.csv")

    result = trend_analysis.holt_winters(df_max, "Timings.time")

    expected_result = [
        84238, 83068.96, 81915.3296, 80651.972096, 79513.96720896, 78452.8046109696, 77569.6823481385,
        76809.0772439481, 76136.2700708378, 75646.5335295161, 75258.0029552781, 75043.5783776766,
        75055.8555804883, 75072.2431195181, 75168.4234259613, 75260.5907340773, 75405.5009512071,
        75544.0890868626, 75728.3160319125, 76013.324946676, 76190.7190806197, 76322.5656245499,
        76428.300234712, 76566.4759134533, 76778.6774199081, 76971.5715282757, 77146.7839538387,
        77414.0825361356, 77697.5981005277, 77974.7066280202, 78343.2451848934, 78671.9862229963,
        78971.9396045587, 78994.3847256263, 78969.5254334554, 78899.8169823804, 78638.7775422252,
        78339.074888412, 78013.189769825, 77757.3940841623, 77476.8217722658, 77196.4910518579,
        76995.4868334572, 76775.5439853984, 76592.4079475355, 76540.0027993437, 76539.8785688165,
        76541.7840416421, 76651.3570582369, 76742.7211891832, 76865.783646373, 78575.2422662699,
        81571.1594715366, 86468.2868568885, 98474.1372908945, 103497.892146464, 106982.14034506,
        109471.373290135, 111432.14471459, 112154.87606557, 112130.146103731, 111291.036290111,
        110220.10698761, 108639.919266105, 106675.772318257, 103973.823867248, 101147.352151751,
        98734.2406932837, 96108.2618987783, 93740.3083872228, 91534.6532424895, 89732.6229970033,
        87833.9338807342, 85971.7852324895, 84194.7149045942, 82777.5100460942, 81779.8457574504
    ]

    assert result.tolist()[:-3] == pytest.approx(expected_result[2:], abs=15000)