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
compression_fractor_VIS   = 3
frame_time_VIS            = 0.2 #sec
stored_frames_per_int_VIS = 1
pass_time_min             = 8
regions_NIR               = 1
bits_per_pix_NIR          = 16
compression_fractor_NIR   = 2

p = ps.PandoraSat()
VIS_ra_shape = p.VISDA.shape[0] * p.VISDA.pixel_scale /3600
VIS_dec_shape = p.VISDA.shape[1] * p.VISDA.pixel_scale /3600
NIR_ra_shape = p.NIRDA.shape[0] * p.NIRDA.pixel_scale /3600
NIR_dec_shape = p.NIRDA.shape[1] * p.NIRDA.pixel_scale /3600


# -

def generate_task_plan(variables, output_file):
    
    template_str = '''<?xml version="1.0" ?>
<ScienceCalendar xmlns="/pandora/calendar/">
<Meta Valid_From="2025-04-25 00:00:00" Expires="2026-04-24 12:29:00" Calendar_Weights="0.0, 0.0, 1.0" Ephemeris="sma=6828.14, ecc=0.0, inc=97.2188, aop=0.0, raan=303.263, ta=0.0" Keepout_Angles="90.0, 40.0, 63.0" Created="2024-03-15 14:20:52.506870" Delivery_Id=""/>
    <Visit>
        <ID>{visit_id}</ID>
        <Observation_Sequence>
            <ID>{obs_id}</ID>
            <Observational_Parameters>
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
            <Payload_Parameters>
                <NIRDA>
                    <AverageGroups>{NIR_AvgGroups}</AverageGroups>
                    <ROI_StartX>{NIR_ROI_StartX}</ROI_StartX>
                    <ROI_StartY>{NIR_ROI_StartY}</ROI_StartY>
                    <ROI_SizeX>{NIR_ROI_SizeX}</ROI_SizeX>
                    <ROI_SizeY>{NIR_ROI_SizeY}</ROI_SizeY>
                    <SC_Resets1>{NIR_SC_Resets1}</SC_Resets1>
                    <SC_Resets2>{NIR_SC_Resets2}</SC_Resets2>
                    <SC_DropFrames1>{NIR_SC_DropFrames1}</SC_DropFrames1>
                    <SC_DropFrames2>{NIR_SC_DropFrames2}</SC_DropFrames2>
                    <SC_DropFrames3>{NIR_SC_DropFrames3}</SC_DropFrames3>
                    <SC_ReadFrames>{NIR_SC_ReadFrames}</SC_ReadFrames>
                    <TargetID>{NIR_targetID}</TargetID>
                    <SC_Groups>{NIR_SC_Groups}</SC_Groups>
                    <SC_Integrations>{NIR_SC_Integrations}</SC_Integrations>
                </NIRDA>
                <VDA>
                    <StartRoiDetMethod>{VIS_StartRoiDetMethod}</StartRoiDetMethod>
                    <FramesPerCoadd>{VIS_FramesPerCoadd}</FramesPerCoadd>
                    <NumTotalFramesRequested>{VIS_NumTotalFramesRequested}</NumTotalFramesRequested>
                    <TargetRA>{VIS_TargetRA}</TargetRA>
                    <TargetDEC>{VIS_TargetDEC}</TargetDEC>
                    <IncludeFieldSolnsInResp>{VIS_IncludeFieldSolnsInResp}</IncludeFieldSolnsInResp>
                    <StarRoiDimension>{VIS_StarRoiDimension}</StarRoiDimension>
                    <MaxNumStarRois>{VIS_MaxNumStarRois}</MaxNumStarRois>
                    <numPredefinedStarRois>{VIS_numPredefinedStarRois}</numPredefinedStarRois>
                    <PredefinedStarRoiRa>{VIS_PredefinedStarRoiRa}</PredefinedStarRoiRa>
                    <PredefinedStarRoiDec>{VIS_PredefinedStarRoiDec}</PredefinedStarRoiDec>
                    <TargetID>{VIS_targetID}</TargetID>
                    <NumExposuresMax>{VIS_NumExposuresMax}</NumExposuresMax>
                    <ExposureTime_us>{VIS_ExposureTime_us}</ExposureTime_us>
                </VDA>
            </Payload_Parameters>
        </Observation_Sequence>'''
    
    # Substitute variables in the template string
    formatted_str = template_str.format(**variables)

    # Save the formatted string to a file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(formatted_str)


