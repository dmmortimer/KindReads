require 'net/http'
require 'uri'
require 'json'
require 'csv'
require 'pry'
require 'date'

class Fopla
	class << self

    API_KEY = #TOKEN

		def perform(path_to_csv)
      start_time = Time.now
      genre = path_to_csv

			isbn_array = []
			isbns_not_found = []

      complete_book_profiles = []
      incomplete_book_profiles = []
      not_found_book_profiles = []

      CSV.foreach(path_to_csv + ".csv") do |row|
        isbn_array.push(row[0])
      end

			isbn_array.compact.uniq.each do |isbn|
        puts "Generating book profile for ISBN: #{isbn}..."
				book_profile = get(isbn)

				if book_profile['book']
          formatted_book_profile = format(book_profile)
          case formatted_book_profile['status']
          when 'complete'
            complete_book_profiles.push(formatted_book_profile)
          else
            incomplete_book_profiles.push(formatted_book_profile)
          end
				else
          isbns_not_found.push(isbn)
          not_found_book_profiles.push(book_profile)
          puts "Could not generate book profile matching #{isbn}"
				end
        sleep 1
			end

      book_profile_types = {
        complete: complete_book_profiles,
        incomplete: incomplete_book_profiles,
        not_found: not_found_book_profiles
      }

      book_profile_types.each do |type, book_profiles|
        next if book_profiles.empty?
        write_to_csv(type.to_s, book_profiles, genre)
      end

      end_time = Time.now

      puts "---\nRESULTS -\nComplete Book Profiles: #{complete_book_profiles.count}\n"\
      "Incomplete Book Profiles: #{incomplete_book_profiles.count}\n"\
      "Books Not Found: #{not_found_book_profiles.count}\n---\n"\
      "Runtime: #{end_time - start_time} seconds"
		end

		private

		def get(isbn)
			endpoint = "https://api2.isbndb.com/book/#{isbn}?with_prices=1"
			uri = URI.parse(endpoint)
			request = Net::HTTP::Get.new(uri)
			request["Accept"] = "application/json"
			request["Authorization"] = API_KEY

			req_options = {
			  use_ssl: uri.scheme == "https",
			}

			response = Net::HTTP.start(uri.hostname, uri.port, req_options) do |http|
			  http.request(request)
			end

			if response.code == '200'
				response = JSON.parse(response.body)
				response['errorType'] ? {} : response
			else
        {
          isbn: isbn,
          title: '*Could not find in database, error '+response.code,
          authors: '',
          publish_date: '',
          publisher: '',
          image: '',
          synopsys: '',
        }
			end
		end

		def format(book_profile)
			profile = book_profile['book']

			formatted_book_profile = {
				isbn: profile['isbn13'] || profile['isbn'],
				title: profile['title'] || 'N/A',
				authors: format_authors(profile),
				publish_date: format_publish_date(profile),
				publisher: profile['publisher'] || 'N/A',
				image: profile['image'] || 'N/A',
				synopsys: profile['synopsys'] || profile['overview'] || double_check_isbn_13(profile),
				weight: format_weight(profile),
			}


      formatted_book_profile['status'] =
        if formatted_book_profile[:authors].downcase == 'n/a' || formatted_book_profile[:image].downcase == 'n/a'
         'incomplete'
      else
        'complete'
      end

      formatted_book_profile
		end

    def format_weight(profile)
      if profile['dimensions_structured'] && profile['dimensions_structured']['weight']
        if profile['dimensions_structured']['weight']['unit'] == 'pounds'
          weight_pounds = profile['dimensions_structured']['weight']['value']
          weight_grams = weight_pounds*454
          weight_grams_rounded = weight_grams.round()
          weight_grams_rounded
        else
          puts "Unrecognized weight units #{profile['dimensions_structured']['weight']['unit']}, weight set to 0"
          0
        end
      else
        0
      end
    end

    def format_publish_date(profile)
      if profile['publish_date']
        Date.parse(profile['publish_date']).strftime("%m/%d/%Y")
      else
        'N/A'
      end
    rescue
      'N/A'
    end

    def format_authors(profile)
      if profile['authors'] && !profile['authors'].empty?
        profile['authors']&.compact.map do |author|
          author.split(', ').reverse.join(' ')
        end.join(', ')
      else
        'N/A'
      end
    end

		def double_check_isbn_13(profile)
			isbn_13 = profile['isbn13']
			new_profile = get(isbn_13)['book']
			new_profile['synopsys'] || new_profile['overview'] || ''
		rescue
			''
		end

		def write_to_csv(type, book_profiles, genre)
      CSV.open(
        "#{Date.today}-FOPLA-#{type}-book-profiles-#{genre}.csv",
        'w',
        write_headers: true,
        headers: [
          'Handle',
          'Title',
          'Body (HTML)',
          'Vendor',
          'Type',
          'Tags',
          'Published',
          'Option1 Name',
          'Option1 Value',
          'Option2 Name',
          'Option2 Value',
          'Option3 Name',
          'Option3 Value',
          'Variant SKU',
          'Variant Grams',
          'Variant Inventory Tracker',
          'Variant Inventory Qty',
          'Variant Inventory Policy',
          'Variant Fulfillment Service',
          'Variant Price',
          'Variant Compare At Price',
          'Variant Requires Shipping',
          'Variant Taxable',
          'Variant Barcode',
          'Image Src',
          'Image Position',
          'Image Alt Text',
          'SEO Title',
        ]
      ) do |csv|
        book_profiles.each do |profile|
          csv << [
            profile[:isbn],
            profile[:title],
            generate_html_body(profile),
            profile[:authors],
            'Book',
            '',
            'TRUE',
            'Title',
            'Default Title',
            '',
            '',
            '',
            '',
            profile[:isbn],
            profile[:weight],
            'shopify',
            '1',
            'deny',
            'manual',
            '',
            '',
            '',
            '',
            profile[:isbn],
            profile[:image],
            '1',
            '',
            '',
          ]
        end
      end
		end

		def generate_html_body(profile)
      formatted = profile[:synopsys].downcase.split(/(?<=[?.!])\s*/).map(&:capitalize).join(" ")
			"#{formatted}<br><br><strong>Publisher: </strong>#{profile[:publisher]}"
		end
	end
end

Fopla.perform('scans')
