##############################################
# $Id: myUtilsTemplate.pm 21509 2020-03-25 11:20:51Z rudolfkoenig $
#
# Save this file as 99_myUtils.pm, and create your own functions in the new
# file. They are then available in every Perl expression.

package main;

use strict;
use warnings;

sub
myUtils_Initialize($$)
{
  my ($hash) = @_;
}

# Enter you functions below _this_ line.
# SAFT_BMM_Readings out of logfilr
# 2024-08-01_23:18:00 SAFT_BMM sOC: 68 internalBatteryVoltage: 523.3 internalBatteryCurrent: -0.5 batterySystemMode: 3 rawBatteryContactorsStatus: 1 IMD: 50.0 VMD: 420.0 PMD: 25570 batteryRequests: 0 IMRContinuous: 23.0 IMR: 29.0 VMR: 560.0 PMR: 15310 globalBatteryStatus: 0 sOCThreshold: 81 

sub create_SAFT_BMM_Readings($)
{
	my $SELF = shift;
	# Log(3,"aufgerufen... $SELF");
	my @readingnames = (
	'SOC',
	'internalBatteryVoltage',
	'internalBatteryCurrent',
	'batterySystemMode',
	'rawBatteryContactorsStatus',
	'IMD',
	'VMD',
	'PMD',
	'batteryRequests',
	'IMRContinuous',
	'IMR',
	'VMR',
	'PMR',
	'globalBatteryStatus',
	'sOCThreshold',
	 );
	my $timestamp = substr(TimeNow(),0,7);
	my $filename = "/opt/fhem/log/SAFT_BMM-$timestamp.log";
	my $last_line = `tail -1 $filename`;
	# Log(3,"last_line... $last_line");
	my @readings  = $last_line =~ /:\s(-?\d+\.?\d*)/g;
	# Log(3,"readings... @readings");
	my $x=0;

	foreach (@readings)
		{
    	# Log(3,"foreach... $x of @readings");
 		my $y = sprintf("%02d",$x);
 		my $readingname = $y."_Reading_$y";
 		$readingname = $y."_".$readingnames[$x] if defined $readingnames[$x];
 		fhem("setreading $SELF $readingname $_");
 		$x++;
 		}
}

# don't change below
1;
