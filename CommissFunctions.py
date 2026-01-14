import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from astropy.time import Time
from tqdm import tqdm
from matplotlib.patches import Rectangle
from astropy.io import fits
import pandorasat as ps

# +
''' Constants ''' 

data_rate                 = 5  
bits_per_pix_VIS          = 32
compression_fractor_VIS   = (1/0.4) #3
frame_time_VIS            = 0.2 #sec
stored_frames_per_int_VIS = 1
pass_time_min             = 8
regions_NIR               = 1
bits_per_pix_NIR          = 16
compression_fractor_NIR   = (1/0.6) #2

p = ps.PandoraSat()
VIS_ra_shape = (p.VISDA.shape[0]*u.pix) * p.VISDA.pixel_scale #arsecs 
VIS_dec_shape = (p.VISDA.shape[1]*u.pix) * p.VISDA.pixel_scale #arsecs 
NIR_ra_shape = (p.NIRDA.shape[0]*u.pix) * p.NIRDA.pixel_scale #arsecs 
NIR_dec_shape = (p.NIRDA.shape[1]*u.pix) * p.NIRDA.pixel_scale #arsecs 


# -

def generate_task_plan(variables, output_file):
    if 'heater_4' in variables and variables['heater_4'] == True:
        heater_keys = ('''
            <Bus_Parameters>
                <SET_EPS_OPER_SETPOINTS>
                    <POWER_BOARD_NUM>3</POWER_BOARD_NUM>
                    <HEATER_NUM>4</HEATER_NUM>
                    <SETPOINT>{H4_SetPoint}</SETPOINT>
                    <DEADBAND>{H4_Deadband}</DEADBAND>
                </SET_EPS_OPER_SETPOINTS>
            </Bus_Parameters>
    ''')
    else:
        heater_keys = ('''
    ''')
    if variables['ffi_flag']:
        vis_mode_keys = '''
                <AcquireVisCamImages>
                    <TargetID>{VIS_targetID}</TargetID>
                    <ROI_StartX>384</ROI_StartX>
                    <ROI_StartY>384</ROI_StartY>
                    <ROI_SizeX>1280</ROI_SizeX>
                    <ROI_SizeY>1280</ROI_SizeY>
                    <SendThumbnails>1</SendThumbnails>
                    <ThumbnailCompressionType>1</ThumbnailCompressionType>
                    <RiceX>3</RiceX>
                    <RiceY>11</RiceY>
                    <SaveImagesToDisk>1</SaveImagesToDisk>
                    <NumExposures>{VIS_NumTotalFramesRequested}</NumExposures>
                    <ExposureTime_us>{VIS_ExposureTime_us}</ExposureTime_us>
                </AcquireVisCamImages>
            '''
    elif variables['VIS_ExposureTime_us'] != '' and float(variables['VIS_ExposureTime_us']) > 0:
        if variables['VIS_StarRoiDetMethod'] < 2:
            roi_ras = ""
            roi_decs = ""
            ras = [ra.value if isinstance(ra, u.Quantity) else ra for ra in variables['VIS_PredefinedStarRoiRa']]
            decs = [dec.value if isinstance(dec, u.Quantity) else dec for dec in variables['VIS_PredefinedStarRoiDec']]
            for i in range(len(ras)):
                roi_ras += '                        <RA' + str(i+1) + '>' + str(ras[i]) + '</RA' + str(i+1) +'>\n'
                roi_decs += '                       <Dec' + str(i+1) + '>' + str(decs[i]) + '</Dec' + str(i+1) +'>\n'
            roi_keys = ('''
                    <numPredefinedStarRois>{VIS_numPredefinedStarRois}</numPredefinedStarRois>
                    <PredefinedStarRoiRa>\n'''+roi_ras+'''                    </PredefinedStarRoiRa>
                    <PredefinedStarRoiDec>\n'''+roi_decs+'''                    </PredefinedStarRoiDec>''')
        else:
            roi_keys = ''
        vis_mode_keys = ('''
                <AcquireVisCamScienceData>
                    <IncludeFieldSolnsInResp>{VIS_IncludeFieldSolnsInResp}</IncludeFieldSolnsInResp>
                    <ROI_StartX>384</ROI_StartX>
                    <ROI_StartY>384</ROI_StartY>
                    <ROI_SizeX>1280</ROI_SizeX>
                    <ROI_SizeY>1280</ROI_SizeY>
                    <MaxMagnitudeInQuadCatalog>16.5</MaxMagnitudeInQuadCatalog>
                    <SaveImagesToDisk>1</SaveImagesToDisk>
                    <RiceX>5</RiceX>
                    <RiceY>25</RiceY>
                    <SendThumbnails>0</SendThumbnails>
                    <TargetID>{VIS_targetID}</TargetID>
                    <TargetRA>{VIS_TargetRA}</TargetRA>
                    <TargetDEC>{VIS_TargetDEC}</TargetDEC>
                    <StarRoiDetMethod>{VIS_StarRoiDetMethod}</StarRoiDetMethod>''' + roi_keys + '''
                    <FramesPerCoadd>{VIS_FramesPerCoadd}</FramesPerCoadd>
                    <ExposureTime_us>{VIS_ExposureTime_us}</ExposureTime_us>
                    <MaxNumStarRois>{VIS_MaxNumStarRois}</MaxNumStarRois>
                    <StarRoiDimension>{VIS_StarRoiDimension[0]}</StarRoiDimension>
                    <NumTotalFramesRequested>{VIS_NumTotalFramesRequested}</NumTotalFramesRequested>
                </AcquireVisCamScienceData>
            ''')
    else:
        vis_mode_keys = ''

    if variables['NIR_SC_Integrations'] == '' or variables['NIR_SC_Integrations'] == 0:
        inf_mode_keys = ''
    else:
        inf_mode_keys = ('''
                <AcquireInfCamImages>
                    <AverageGroups>{NIR_AvgGroups}</AverageGroups>
                    <ROI_StartX>{NIR_ROI_StartX}</ROI_StartX>
                    <ROI_StartY>{NIR_ROI_StartY}</ROI_StartY>
                    <ROI_SizeX>{NIR_ROI_SizeX}</ROI_SizeX>
                    <ROI_SizeY>{NIR_ROI_SizeY}</ROI_SizeY>
                    <RiceX>5</RiceX>
                    <RiceY>28</RiceY>
                    <SaveImagesToDisk>1</SaveImagesToDisk>
                    <SendThumbnails>1</SendThumbnails>
                    <ThumbnailBinSize>1</ThumbnailBinSize>
                    <ThumbnailCompressionType>1</ThumbnailCompressionType>
                    <TargetID>{NIR_targetID}</TargetID>
                    <SC_Resets1>{NIR_SC_Resets1}</SC_Resets1>
                    <SC_Resets2>{NIR_SC_Resets2}</SC_Resets2>
                    <SC_DropFrames1>{NIR_SC_DropFrames1}</SC_DropFrames1>
                    <SC_DropFrames2>{NIR_SC_DropFrames2}</SC_DropFrames2>
                    <SC_DropFrames3>{NIR_SC_DropFrames3}</SC_DropFrames3>
                    <SC_ReadFrames>{NIR_SC_ReadFrames}</SC_ReadFrames>
                    <SC_Groups>{NIR_SC_Groups}</SC_Groups>
                    <SC_Integrations>{NIR_SC_Integrations}</SC_Integrations>
                </AcquireInfCamImages>''')

    template_str = ('''<?xml version="1.0" ?>
<ScienceCalendar xmlns="/pandora/calendar/">
<Meta Valid_From="2026-01-05 00:00:00" Expires="2026-02-5 00:00:00" Calendar_Weights="0.0, 0.0, 1.0" Ephemeris="sma=6828.14, ecc=0.0, inc=97.2188, aop=0.0, raan=303.263, ta=0.0" Keepout_Angles="90.0, 25.0, 63.0" Created="2025-09-19 14:20:52.506870" Delivery_Id=""/>
    <Visit>
        <ID>{visit_id}</ID>
        <Observation_Sequence>
            <ID>{obs_id}</ID>''' + heater_keys +
'''        <Observational_Parameters>
                <Target>{target}</Target>
                <Priority>{priority}</Priority>
                <Timing>
                    <Start>{start_time}</Start>
                    <Stop>{stop_time}</Stop>
                </Timing>
                <Boresight>
                    <RA>{RA}</RA>
                    <DEC>{DEC}</DEC>
                </Boresight>
            </Observational_Parameters>
            <Payload_Parameters>''' + inf_mode_keys + vis_mode_keys +
                # <AcquireInfCamImages>
                #     <AverageGroups>{NIR_AvgGroups}</AverageGroups>
                #     <IncludeFieldSolnsInResp>1</IncludeFieldSolnsInResp>
                #     <ROI_StartX>{NIR_ROI_StartX}</ROI_StartX>
                #     <ROI_StartY>{NIR_ROI_StartY}</ROI_StartY>
                #     <ROI_SizeX>{NIR_ROI_SizeX}</ROI_SizeX>
                #     <ROI_SizeY>{NIR_ROI_SizeY}</ROI_SizeY>
                #     <TargetID>{NIR_targetID}</TargetID>
                #     <SC_Resets1>{NIR_SC_Resets1}</SC_Resets1>
                #     <SC_Resets2>{NIR_SC_Resets2}</SC_Resets2>
                #     <SC_DropFrames1>{NIR_SC_DropFrames1}</SC_DropFrames1>
                #     <SC_DropFrames2>{NIR_SC_DropFrames2}</SC_DropFrames2>
                #     <SC_DropFrames3>{NIR_SC_DropFrames3}</SC_DropFrames3>
                #     <SC_ReadFrames>{NIR_SC_ReadFrames}</SC_ReadFrames>
                #     <SC_Groups>{NIR_SC_Groups}</SC_Groups>
                #     <SC_Integrations>{NIR_SC_Integrations}</SC_Integrations>
                # </AcquireInfCamImages>''' + vis_mode_keys +
         '''</Payload_Parameters>
        </Observation_Sequence>
    </Visit>
</ScienceCalendar>''')

    # Substitute variables in the template string
    formatted_str = template_str.format(**variables)

    # Save the formatted string to a file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(formatted_str)

