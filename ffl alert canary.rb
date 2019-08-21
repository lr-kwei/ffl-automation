## INPUTS ##
ACXIOM_CUSTOMER = 511196
ADA_FIELD_ACTIVE = AdaField.statuses.active
ADA_ACTIVE = AudienceDestinationAccount.statuses.active
DA_ACTIVE = DestinationAccount.statuses.active
SSA_ACTIVE = ServerSideAccount.statuses.active
DSJ_STEP_DONE = DataSyncJob.steps.done
DSJ_STATUS_COMPLETE = DataSyncJob.statuses.completed
DSJ_STATUS_PENDING = [DataSyncJob.statuses.pending, DataSyncJob.statuses.in_progress, DataSyncJob.statuses.ready]
SSA_REFRESH_REQUEST_PENDING = [SsaRefreshRequest.statuses.pending, SsaRefreshRequest.statuses.in_progress]

PUBS = [
	{:name => "Twitter", :aud => 156426, :logo => "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMK4p7YJ2ABCissS-vYpzZXTKlnyyH6VqeLRe0T4gpxIrSNEuonNUeG3w"},
	{:name => "MSN", :aud => 162186, :logo => "http://ncmedia.azureedge.net/ncmedia/2015/01/MSN_Blue_RGB1.png"},
	{:name => "NinthDecimal", :aud => 156466, :logo => "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQY-VBIEnCxvcVWQqkXubKrbCngeJmPI_8huviUFIFA4IH7Hu0"},
	{:name => "4INFO", :aud => 156456, :logo => "http://ww1.prweb.com/prfiles/2014/09/29/12406924/4INFO%20Logo.jpg"},
	{:name => "eBay", :aud => 156476, :logo => "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYcpQ2_Be_TX8RUNtlZBkAd82Y5jOhSdQABqMf_S_pJ-dH73dIo-Xwursw"},
	{:name => "Yahoo", :aud => 156446, :logo => "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Yahoo_Logo.svg/2000px-Yahoo_Logo.svg.png"},
	{:name => "AOL", :aud => 156436, :logo => "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/AOL_logo.svg/2000px-AOL_logo.svg.png"},
	{:name => "Facebook", :aud => 156416, :logo => "http://www.freeiconspng.com/uploads/facebook-announces-clickable-hashtags--resolution-media-17.png"}
]

OMITTED_LRCF_ID = [
    19417166 # Package U4563215 - strange FB one that was sent through the API but we didn't get a distribution email
    ]

## HTML STRINGS AND METHODS##
# style constants
WHITE = "color: #ffffff"
GREEN = "color: #339966"
ORANGE = "color: #ff9900"
RED = "color: #ff0000"
CENTER = "text-align: center" #general centering
RISK_PROFILE = [3,10] #anything lower than first element is low risk, anything in middle is medium, anything above second element is high risk

# table constants
# table html that takes [header row, rows] as input
TABLE = "<table cellpadding=\"3\" style=\"border-color: #000000;\" border=\"1\"><thead>%s</thead><tbody>%s</tbody></table>"
ELAPSED_CELL = "<span style=\"%s\">%s</span>"

# array of column elements
def make_header_row(column_elements)
	"<tr style=\"background-color: #808080;\"><td style=\"#{CENTER};\"><span style=\"#{WHITE};\"><strong>
		#{column_elements.join("</strong></span></td><td style=\"#{CENTER};\"><span style=\"#{WHITE};\"><strong>")}
		</strong></span></td></tr>"
end

# array of column elements
def make_row(column_elements)
	"<tr><td>#{column_elements.join("</td><td>")}</td></tr>"
end


# segment elapsted html
def segment_elapsed_cell(seg,delivery_time = Time.now)
	elapsed = delivery_time-seg.created_at
	human_elapsed = humanize_time(elapsed)
	case elapsed/3600 #for hours
	when 0..RISK_PROFILE.first then #low risk
		ELAPSED_CELL % [GREEN , human_elapsed]
	when RISK_PROFILE.first .. RISK_PROFILE.last #medium risk
		ELAPSED_CELL % [ORANGE , human_elapsed]
	else #high risk
		ELAPSED_CELL % [RED , human_elapsed]
	end
end

# makes any number of seconds human readable
def humanize_time(seconds)
	minutes = seconds / 60
  	[[60, :m], [24, :h], [100000, :d]].map{ |count, name|
    if minutes > 0
      minutes, n = minutes.divmod(count)
      "#{n.to_i}#{name}"
    end
  }.compact.reverse.join('')
end

# segments requiring DA
def segments_requiring_da_table(ds_segs)
	header = make_header_row(["!!!!","DS Segment ID","Package ID","Field / Value","DS Segment Name"])
	rows = ds_segs.reverse.map{|ds_seg| make_row([segment_elapsed_cell(ds_seg),
						ds_seg.id,
						ds_seg_package_ID(ds_seg),
						"#{ds_seg.lrc_field_definition_id}/#{ds_seg.liveramp_field_value_id}",
						ds_seg.segment_name])}.join
	TABLE % [header,rows]
end

def das_needing_backfill_table(ds_segs)
	header = make_header_row(["Package_ID (DA ID)","!!!!","DS Segment ID","SSA"])
	rows = ds_segs.reverse.group_by(&:second).map{|da,segs| make_row(["#{DA_LINK % [da.id,"overview","#{da.name} (#{da.id})"]}",
			segment_elapsed_cell(segs.first.first),
			segs.map(&:first).map(&:id).join("<br>"),
			segs.map(&:last).uniq.join("<br>")
		])}.join
	TABLE % [header,rows]
end

def das_requiring_attention_table(ds_segs)
	header = make_header_row(["Package_ID (DA ID)","!!!!","DS Segment ID","Note"])
	rows = ds_segs.reverse.group_by(&:second).map{|da,segs| make_row(["#{DA_LINK % [da.id,"overview","#{da.name} (#{da.id})"]}",
			segment_elapsed_cell(segs.first.first),
			segs.map(&:first).map(&:id).uniq.join("<br>"),
			segs.map(&:last).uniq.join("<br>")
		])}.join
	TABLE % [header,rows]
end

def segments_pending_delivery_table(ds_segs)
	header = make_header_row(["Package_ID (DA ID)","!!!!","DS Segment ID","Note"])
	rows = ds_segs.reverse.group_by(&:second).map{|da,segs| make_row(["#{DA_LINK % [da.id,"overview","#{da.name} (#{da.id})"]}",
			segment_elapsed_cell(segs.first.first),
			segs.map(&:first).map(&:id).join("<br>"),
			segs.map(&:last).uniq.join("<br>")
		])}.join
	TABLE % [header,rows]
end

def segments_delivered_table(ds_segs)
	header = make_header_row(["Package_ID (DA ID)","!!!!","DS Segment ID"])
	rows = ds_segs.reverse.group_by(&:second).map{|da,segs| make_row(["#{DA_LINK % [da.id,"overview","#{da.name} (#{da.id})"]}",
			segment_elapsed_cell(segs.first.first,segs.first.last),
			segs.map(&:first).map(&:id).join("<br>")
		])}.join
	TABLE % [header,rows]
end



#email logistics
RECIPIENTS = "premiumpub@liveramp.com, asaraf@liveramp.com"

#links
AUD_LINK = "<a href=\"https://audience.admin.liveramp.net/%s#overview\">%s</a>"
SSA_LINK = "<a href=\"https://destination.admin.liveramp.net/server/%s#%s\">%s</a>" #[ssa_id,tab,link_string]
DA_LINK = "<a href=\"https://destination.admin.liveramp.net/destination_account/%s#%s\">%s</a>" #[da_id,tab,link_string]

# overall email header, takes in [pub name , pub logo url] as inputs
PUB_HEADER = "<h1><em><strong></strong><span style=\"text-decoration: underline;\"><strong>%s</strong></span><strong> <img src=\"%s\" alt=\"\" width=\"30\" height=\"30\"/></strong></em></h1>
	See it all go down on the %s Audience"
# section header, takes in section name as input
SECTION_HEADER_STYLE =  "<h4><span style=\"text-decoration: underline;\"><strong>%s</strong></span></h4>"
# subject
SUBJECT = "[FFL Distributions Alert] %s -- #{Time.now.strftime("%b %e")}"
NEED_BACKFILL_SUBJECT = "[FFL Distribution Alert] These SSAs Need Backfills NOW"

# section discriptions
SEGMENTS_WITHOUT_DA_SECTION = SECTION_HEADER_STYLE % "Segments Requiring DA setup" +
	"<strong><span style=\"#{RED};\">WARNING! </span></strong>These %s segments need a DA <span style=\"#{RED};\"><strong>NOW</strong></span>.
	Please setup a DA for these"

DAS_REQUIRING_BACKFILL = SECTION_HEADER_STYLE % "Segments whose DAs/SSAs need a backfill" +
	"<strong><span style=\"#{RED};\">WARNING! </span></strong>These %s segments need a backfill <span style=\"#{RED};\"><strong>NOW</strong></span>.
	Please backfill these %s DAs/SSAs"

DAS_REQUIRING_ATTENTION = SECTION_HEADER_STYLE % "Segments whose DAs/SSAs have a strange setup" +
	"<strong><span style=\"#{RED};\">WARNING! </span></strong>These %s segments have DA/SSA setups that are off and need attention <span style=\"#{RED};\"><strong>NOW</strong></span>.
	Please look at the \"Note\" column of the below tablet to fix these %s DAs"

SEGMENTS_NOT_READY_WITHOUT_DA_SECTION = SECTION_HEADER_STYLE % "Segments that aren't ready but need a DA setup" +
	"These %s segments need a DA <strong>soon</strong>.	Please remedy setup a DA for these"

DAS_PENDING_DELIVERY = SECTION_HEADER_STYLE % "Segments Pending Delivery" +
	"These %s segments are currently deliverying.  You might wanna up DSJ priorities on any whose elapsed time is too old"

SEGMENTS_DELIVERED = SECTION_HEADER_STYLE % "Segments Delivered" +
	"These %s segments have been delivered.  Good job!"


## HELPER METHODS ##
def get_dms_segments(aud)
	allfields = aud.lrc_field_definitions.select{|lrcf| lrcf.enabled}.
		reject{|lrcf| OMITTED_LRCF_ID.include? lrcf.id}
	recentfields = []
	allfields.each do |field|
		if field.created_at.between?(30.days.ago, Time.now)
			recentfields << field
		end
	end
	recentfields.map(&:dms_segments).flatten.
		select{|dms_seg| dms_seg.enabled};
end

def segment_ready_for_delivery?(seg)
	seg.lrc_field_definition.lir_fields.first.liveramp_import_request.
		liveramp_import_request_events.select{|lire| lire.app_type == 910 && lire.app_status == 2}.
		count > 0 ? true : false
end

def get_das_on_segment(seg)
	seg.lrc_field_definition.ada_fields.select{|ada_field| ada_field.status == ADA_FIELD_ACTIVE}.
		map(&:audience_destination_account).select{|ada| ada.status == ADA_ACTIVE}.
		map(&:destination_account).select{|da| da.status == DA_ACTIVE} || []
end

def get_ssas_on_da_on_segment(da)
	da.server_side_accounts.select{|ssa| ssa.status == SSA_ACTIVE} || []
end

def check_ssa_delivery_status(ssa,seg)
	state = [ssa.data_sync_jobs.select{|dsj| dsj.step == DSJ_STEP_DONE && dsj.status == DSJ_STATUS_COMPLETE}.count, #complete DSJs
			ssa.data_sync_jobs.select{|dsj| DSJ_STATUS_PENDING.include? dsj.status}.count, #pending_DSJs
			ssa.ssa_refresh_requests.select{|rr| SSA_REFRESH_REQUEST_PENDING.include? rr.status}.count] #pending SSA Refresh Requests

	case state
		when [1,0,0] #1 completed dsj, 0 pending dsjs or refresh requests
			ssa.data_sync_jobs.select{|dsj| dsj.step == DSJ_STEP_DONE && dsj.status == DSJ_STATUS_COMPLETE}.first.updated_at
		when [0,1,0], [0,0,1]  #1 pending dsjs or refresh requests and 0 completed dsjs
			"pending"
		when [0,0,0] #0 completed dsjs and 0 pending dsjs or refresh requests
			segment_ready_for_delivery?(seg) ? "requires_backfill" : "pending"
		else #something is strange and need to take a look ASAP
			"strange"
	end
end

def ds_seg_package_ID(seg)
	seg.lrc_field_definition.label.split("_").first
end
####

need_backfills = [] # array of all SSAs that need backfills
emails = [] # array of email contents


#loop through publishers
PUBS.each do |pub|
	#pub = PUBS["Twitter"]

	#grab audience (with a ton of includes)
	aud = LiverampCustomerAccount.where(:id => pub.aud).
			includes(:lrc_field_definitions => [:dms_segments,
				:ada_fields => [:ada_field_values , :audience_destination_account =>
						[:destination_account =>
							[:server_side_accounts =>
								[:ssa_refresh_requests, :data_sync_jobs]]]]]).
			includes(:lrc_field_definitions => [:lir_fields =>
				[:liveramp_import_request => :liveramp_import_request_events]]).first
			#where("lrc_field_definitions.enabled" => true,
			#	"dms_segments.enabled" => true,
			#	"ada_fields.status" => ADA_FIELD_ACTIVE,
			#	"audience_destination_accounts.status" => ADA_ACTIVE,
			#	"destination_accounts.status" => DA_ACTIVE,
			#	"server_side_accounts.status" => SSA_ACTIVE).first
	###


	#initalize arrays for pub segments
	segments_ready_without_das = [] # segments that have gone through AC but aren't configured in a DA
	segments_not_ready_without_das = [] # segments that haven't gone through AC and aren't configured in a DA
	segments_with_strange_da_setup = [] # example 2 or 0 SSAs on DA
	segments_with_ssas_actively_refresh_on = [] # segments where the SSAs have active refresh on
	segments_delivered = [] # segments delivered just fine
	segments_with_strange_delivery_profile = [] # segments with multiple backfills/dsjs or general things strange
	segments_pending_delivery = [] # segments where delivery is going or they're not through AC
	segments_needing_backfill = [] # segments where SSA is good to go but they need backfill


	#grab segments and loop through them
	segs = get_dms_segments(aud)


	segs.each do |seg|

		#seg = segs.first

		#get DAs for this segment
		das = get_das_on_segment(seg)

		#if no DAs, add to correct array
		if das == []
			if segment_ready_for_delivery?(seg)
				segments_ready_without_das << seg
			else
				segments_not_ready_without_das << seg
			end
			next
		end

		# loop through DAs and analyze
		das.each do |da|
			#check for strange SSA setup
			ssas = get_ssas_on_da_on_segment(da)

			#check for multiple or no SSAs on the DA
			if ssas.count == 0 || ssas.count > 1
				segments_with_strange_da_setup << [seg,da,"DA has #{ssas.count} SSAs (should have 1)"]
				next
			end

			ssas.each do |ssa|
				#check for active refresh
				segments_with_ssas_actively_refresh_on << [seg,da,"#{SSA_LINK % [ssa.id,"configuration","SSA#{ssa.id}"]} has active refresh on (please turn off)"] if ssa.refreshed_daily

				#check if there is a state of delivery
				state = check_ssa_delivery_status(ssa,seg)

				case state
					when "pending"
						segments_pending_delivery << [seg,da,"#{SSA_LINK % [ssa.id,"delivery","SSA#{ssa.id}"]}"]
					when "requires_backfill"
						segments_needing_backfill << [seg,da,"#{SSA_LINK % [ssa.id,"delivery","SSA#{ssa.id}"]}"]
						need_backfills << ssa.id
					when "strange"
						segments_with_strange_delivery_profile << [seg,da,"#{SSA_LINK % [ssa.id,"delivery","SSA#{ssa.id}"]} has a strange delivery profile"]
					else
						segments_delivered << [seg,da,check_ssa_delivery_status(ssa,seg)]
				end
			end
		end
	end

	body = PUB_HEADER % [pub.name, pub.logo, AUD_LINK % [pub.aud,pub.name]]

	# segments requiring DA setup section
	unless segments_ready_without_das.empty?
		body += SEGMENTS_WITHOUT_DA_SECTION % segments_ready_without_das.length
		body += segments_requiring_da_table(segments_ready_without_das)
	end

	unless segments_needing_backfill.empty?
		body += DAS_REQUIRING_BACKFILL % [segments_needing_backfill.length, segments_needing_backfill.map(&:second).uniq.length]
		body += das_needing_backfill_table(segments_needing_backfill)
	end

	segments_requiring_attention = segments_with_strange_da_setup + segments_with_ssas_actively_refresh_on + segments_with_strange_delivery_profile
	unless segments_requiring_attention.empty?
		body += DAS_REQUIRING_ATTENTION % [segments_requiring_attention.length, segments_requiring_attention.map(&:second).uniq.length]
		body += das_requiring_attention_table(segments_requiring_attention)
	end

	unless segments_not_ready_without_das.empty?
		body += SEGMENTS_NOT_READY_WITHOUT_DA_SECTION % segments_not_ready_without_das.length
		body += segments_requiring_da_table(segments_not_ready_without_das)
	end

	unless segments_pending_delivery.empty?
		body += DAS_PENDING_DELIVERY % segments_pending_delivery.length
		body += segments_pending_delivery_table(segments_pending_delivery)
	end

	unless segments_delivered.empty?
		body += SEGMENTS_DELIVERED % segments_delivered.length
		body += segments_delivered_table(segments_delivered)
	end


	emails << {
	   :emails => RECIPIENTS,
	   :body => body,
	   :subject => SUBJECT % pub.name
	}

end

#one last email for all needed backfills
if need_backfills.any?
    emails << {
        :emails  => RECIPIENTS,
        :body => need_backfills.uniq.join(", "),
        :subject => NEED_BACKFILL_SUBJECT
    }
end

return emails
